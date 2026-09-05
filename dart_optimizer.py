"""
Dart-throw aim-point optimizer
--------------------------------
Given:
  - your throw's scatter, modeled as a 2D Gaussian with std devs sigma_x, sigma_y (mm),
    assumed independent in x and y
  - a target region on the board, defined as a 0/1 mask over an x,y grid (g(x,y))

This script computes, for every candidate aim point on the board, the probability
that a dart aimed there lands in the target region -- then finds the best one
and plots the whole probability surface as a heatmap.

Coordinates: origin (0,0) = center of the board (the bullseye). Units: mm.
Angle convention: theta = 0 points straight up (towards the "20"), increasing
clockwise, matching how a real dartboard is numbered.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
from notebook.explore import numbers as valid_numbers


# ----------------------------------------------------------------------
# 1. Dartboard geometry (standard mm dimensions, origin = board center)
# ----------------------------------------------------------------------
BULL_R        = 6.35     # inner bull / "double bull" (50 pts)
OUTER_BULL_R  = 15.9     # outer bull / "single bull" (25 pts)
TRIPLE_IN     = 99.0
TRIPLE_OUT    = 107.0
DOUBLE_IN     = 162.0
DOUBLE_OUT    = 170.0    # outside this radius = miss

SEGMENT_ORDER = [20, 1, 18, 4, 13, 6, 10, 15, 2, 17, 3, 19, 7, 16, 8, 11, 14, 9, 12, 5]
SEG_WIDTH = 18.0  # degrees per number wedge (360 / 20 numbers)


def segment_number(x, y):
    """Which number wedge (1-20) a point falls in. theta=0 is straight up, clockwise+."""
    theta = np.degrees(np.arctan2(x, y)) % 360
    idx = (((theta + SEG_WIDTH / 2) // SEG_WIDTH).astype(int)) % 20
    lookup = np.array(SEGMENT_ORDER)
    return lookup[idx]


def score_grid(X, Y):
    """Bonus/reference: the actual dart SCORE at every (x,y) point (0 = miss).
    Swap this in later if you want to maximize *expected score* instead of the
    probability of hitting one specific region -- same machinery, different g."""
    R = np.sqrt(X ** 2 + Y ** 2)
    number = segment_number(X, Y)
    mult = np.ones_like(R)
    mult[(R >= TRIPLE_IN) & (R <= TRIPLE_OUT)] = 3
    mult[(R >= DOUBLE_IN) & (R <= DOUBLE_OUT)] = 2
    score = number.astype(float) * mult
    score[R <= OUTER_BULL_R] = 25
    score[R <= BULL_R] = 50
    score[R > DOUBLE_OUT] = 0
    return score


# ----------------------------------------------------------------------
# 2. Build the grid
# ----------------------------------------------------------------------
GRID_HALF_WIDTH = 200      # mm; board radius is 170mm, extra margin for Gaussian tails
RES = 0.5                  # mm per grid cell -- finer = more accurate, slower
coords = np.arange(-GRID_HALF_WIDTH, GRID_HALF_WIDTH + RES, RES)
X, Y = np.meshgrid(coords, coords)   # X, Y = mm position of every grid cell
cell_area = RES ** 2

# ----------------------------------------------------------------------
# 3. Define your target region: g(x,y) = 1 inside, 0 outside.
#    Example here: the triple-20 bed. Swap this out for whatever you're aiming
#    to hit -- it's just a boolean condition on X, Y.
# ----------------------------------------------------------------------
R = np.sqrt(X ** 2 + Y ** 2)
number = segment_number(X, Y)
def single_region(n):
  return ((number == n) & (R > OUTER_BULL_R) & (R < DOUBLE_IN) & ~((R > TRIPLE_IN) & (R < TRIPLE_OUT)))

def double_region(n):
  return ((number == n) & (R > DOUBLE_IN) & (R < DOUBLE_OUT))

def triple_region(n):
  return ((number == n) & (R > TRIPLE_IN) & (R < TRIPLE_OUT))

def region(n):
  s = d = t = False
  if n == 50:
    return (R <= BULL_R)
  if n == 25:
    return (R <= OUTER_BULL_R)
  if n <= 20:
    s = True
  if n % 2 == 0:
    d = True
  if n % 3 == 0:
    t = True
  return (
    (R <= BULL_R) |
    (s * single_region(n)) |
    (d * double_region(n/2)) |
    (t * triple_region(n/3))
  )

target_mask = region(21).astype(float)

# ----------------------------------------------------------------------
# 4. Your throw's spread -- REPLACE these with your own measured values (mm)
# ----------------------------------------------------------------------
sigma_x = sigma_y = 25.0

# ----------------------------------------------------------------------
# 5. METHOD A -- the direct, "by hand" way, for exactly ONE aim point.
#    This is literally: sum( density * cell_area ) over every cell in the
#    target region. Slow if repeated for every aim point, but it's the
#    ground truth, and it's exactly the process we described in words.
# ----------------------------------------------------------------------
"""
def probability_at_aim(aim_x, aim_y, sigma_x, sigma_y, X, Y, mask, cell_area):
    density = (1.0 / (2 * np.pi * sigma_x * sigma_y)) * np.exp(
        -(((X - aim_x) ** 2) / (2 * sigma_x ** 2) + ((Y - aim_y) ** 2) / (2 * sigma_y ** 2))
    )
    return np.sum(density * mask) * cell_area


test_aim = (0.0, 103.0)   # try aiming at the middle of the triple-20 bed (straight up, r~103mm)
p_direct = probability_at_aim(*test_aim, sigma_x, sigma_y, X, Y, target_mask, cell_area)
print(f"Method A (direct sum) at aim={test_aim}: {p_direct:.4f}")
"""
# ----------------------------------------------------------------------
# 6. METHOD B -- the fast way: do that SAME sum for every possible aim
#    point at once, by Gaussian-blurring the target mask. This computes an
#    identical number to Method A at every point simultaneously.
# ----------------------------------------------------------------------
sigma_px = (sigma_y / RES, sigma_x / RES)   # array axis 0 = y, axis 1 = x
P = gaussian_filter(target_mask, sigma=sigma_px, mode='constant')

# sanity check: Method B's value at the same test point should match Method A
"""
iy = np.argmin(np.abs(coords - test_aim[1]))
ix = np.argmin(np.abs(coords - test_aim[0]))
print(f"Method B (blurred grid) at same point:  {P[iy, ix]:.4f}")
"""

# ----------------------------------------------------------------------
# 7. Find the best aim point
# ----------------------------------------------------------------------
best_iy, best_ix = np.unravel_index(np.argmax(P), P.shape)
best_x, best_y = X[best_iy, best_ix], Y[best_iy, best_ix]
best_p = P[best_iy, best_ix]
best_r = np.hypot(best_x, best_y)
best_theta = np.degrees(np.arctan2(best_x, best_y)) % 360

print(f"\nBest aim point: x={best_x:.1f} mm, y={best_y:.1f} mm")
print(f"  (equivalently: r={best_r:.1f} mm, theta={best_theta:.1f} deg clockwise from top)")
print(f"Probability of hitting the target region there: {best_p:.5f}")
# ----------------------------------------------------------------------
# 7b. Look up the probability at ANY specific aim point from the heatmap
#     you already computed -- pass either (x, y) or (r, theta), not both.
# ----------------------------------------------------------------------
def probability_lookup(P, coords, x=None, y=None, r=None, theta=None):
    """Nearest-grid-cell lookup of P at a single aim point.
    theta is in degrees, 0 = straight up, clockwise-positive (matches the board)."""
    if r is not None and theta is not None:
        theta_rad = np.radians(theta)
        x = r * np.sin(theta_rad)
        y = r * np.cos(theta_rad)
    elif x is None or y is None:
        raise ValueError("Provide either (x, y) or (r, theta), not neither")
 
    ix = np.argmin(np.abs(coords - x))
    iy = np.argmin(np.abs(coords - y))
    return P[iy, ix]
 
 
# examples -- both describe the same physical point, so they should agree
p_xy = probability_lookup(P, coords, x=0.0, y=103.0)
p_polar = probability_lookup(P, coords, r=103.0, theta=0.0)
print(f"\nLookup by (x,y):     {p_xy:.4f}")
print(f"Lookup by (r,theta): {p_polar:.4f}")
# ----------------------------------------------------------------------
# 8a. Table 1
# ----------------------------------------------------------------------
# Make a table containing the optimal aim point and win % for each 

# ----------------------------------------------------------------------
# 8b. Plot
# ----------------------------------------------------------------------
"""
fig, ax = plt.subplots(figsize=(7, 7))
im = ax.imshow(
    P, extent=[-GRID_HALF_WIDTH, GRID_HALF_WIDTH, -GRID_HALF_WIDTH, GRID_HALF_WIDTH],
    origin='lower', cmap='viridis'
)
plt.colorbar(im, ax=ax, label='Probability of hitting target region')

theta_circ = np.linspace(0, 2 * np.pi, 200)
ax.plot(DOUBLE_OUT * np.sin(theta_circ), DOUBLE_OUT * np.cos(theta_circ), 'w--', linewidth=0.8)
ax.contour(X, Y, target_mask, levels=[0.5], colors='red', linewidths=1.2)

ax.plot(best_x, best_y, '.', markersize=2, label='optimal aim point')
ax.set_xlabel('x (mm)')
ax.set_ylabel('y (mm)')
ax.set_title('Probability of hitting target region, by aim point')
ax.legend(loc='upper right')
ax.set_aspect('equal')
plt.tight_layout()
plt.savefig('dart_aim_heatmap.png', dpi=150)
print("\nSaved heatmap to dart_aim_heatmap.png")
"""