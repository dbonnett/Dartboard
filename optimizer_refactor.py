import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
from notebook.explore import numbers as valid_numbers

# ----------------------------------------------------------------------
# 1. Dartboard Setup
# ----------------------------------------------------------------------

# Define Dartboard Dimensions
BULL_R        = 6.35
OUTER_BULL_R  = 15.9
TRIPLE_IN     = 99.0
TRIPLE_OUT    = 107.0
DOUBLE_IN     = 162.0
DOUBLE_OUT    = 170.0

SEGMENT_ORDER = [20, 1, 18, 4, 13, 6, 10, 15, 2, 17, 3, 19, 7, 16, 8, 11, 14, 9, 12, 5]
SEG_WIDTH = 18.0  

# which number slice (1-20) based on (x,y) coordinates
def segment_number(x, y):
    theta = np.degrees(np.arctan2(x, y)) % 360
    idx = (((theta + SEG_WIDTH / 2) // SEG_WIDTH).astype(int)) % 20
    lookup = np.array(SEGMENT_ORDER)
    return lookup[idx]

# score based on (x,y) coordinates
def score_grid(X, Y):
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
GRID_HALF_WIDTH = 200
RES = 0.5              
coords = np.arange(-GRID_HALF_WIDTH, GRID_HALF_WIDTH + RES, RES)
X, Y = np.meshgrid(coords, coords)
cell_area = RES ** 2

# ----------------------------------------------------------------------
# 3. Define region for each score n
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

target_mask = region(23).astype(float)

# ----------------------------------------------------------------------
# 4. Define probability distribution
# ----------------------------------------------------------------------
sigma_x = sigma_y = 25.0
sigma_px = (sigma_y / RES, sigma_x / RES)
P = gaussian_filter(target_mask, sigma=sigma_px, mode='constant')

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
# 8b. Plot
# ----------------------------------------------------------------------

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