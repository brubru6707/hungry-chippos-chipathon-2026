import struct
import numpy as np
import matplotlib.pyplot as plt


def parse_ngspice_raw(filepath):
    with open(filepath, "rb") as f:
        raw = f.read()

    binary_marker = b"Binary:\n"
    split = raw.find(binary_marker)
    header = raw[:split].decode("ascii", errors="replace")
    binary_data = raw[split + len(binary_marker):]

    n_vars, n_points = 0, 0
    var_names = []
    in_vars = False
    for line in header.splitlines():
        line = line.strip()
        if line.startswith("No. Variables:"):
            n_vars = int(line.split(":")[1])
        elif line.startswith("No. Points:"):
            n_points = int(line.split(":")[1])
        elif line == "Variables:":
            in_vars = True
        elif in_vars and line and not line.startswith("Binary"):
            parts = line.split()
            var_names.append(parts[1] if len(parts) > 1 else parts[0])
        elif line.startswith("Binary"):
            in_vars = False

    n_values = n_vars * n_points
    values = struct.unpack(f"<{n_values}d", binary_data[:n_values * 8])
    data = np.array(values).reshape(n_points, n_vars)

    return var_names, data


var_names, data = parse_ngspice_raw("comp_mc_offsets.raw")
offsets_v = data[:, 1]
offsets_mv = offsets_v * 1e3

mean_mv = np.mean(offsets_mv)
std_mv = np.std(offsets_mv)
p3sigma = mean_mv + 3 * std_mv
n3sigma = mean_mv - 3 * std_mv

print(f"Monte Carlo Comparator Offset ({len(offsets_mv)} runs)")
print(f"  Mean  : {mean_mv:+.3f} mV")
print(f"  Std   : {std_mv:.3f} mV")
print(f"  3sigma: [{n3sigma:+.3f}, {p3sigma:+.3f}] mV")
print(f"  Min   : {offsets_mv.min():+.3f} mV")
print(f"  Max   : {offsets_mv.max():+.3f} mV")

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
fig.suptitle("Comparator MC Offset Analysis — Post-Fix (N=100)", fontsize=14, fontweight="bold")

ax = axes[0]
n, bins, _ = ax.hist(offsets_mv, bins=20, color="steelblue", edgecolor="white", alpha=0.85)
ax.axvline(mean_mv, color="red", lw=2, linestyle="-", label=f"Mean = {mean_mv:+.2f} mV")
ax.axvline(p3sigma, color="orange", lw=1.5, linestyle="--", label=f"+3σ = {p3sigma:+.2f} mV")
ax.axvline(n3sigma, color="orange", lw=1.5, linestyle="--", label=f"−3σ = {n3sigma:+.2f} mV")
ax.set_xlabel("Offset (mV)")
ax.set_ylabel("Count")
ax.set_title("Offset Histogram")
ax.legend(fontsize=9)

ax = axes[1]
sorted_offsets = np.sort(offsets_mv)
ranks = np.arange(1, len(sorted_offsets) + 1)
ax.plot(ranks, sorted_offsets, "o", color="steelblue", markersize=4, alpha=0.7)
ax.axhline(mean_mv, color="red", lw=2, linestyle="-", label=f"Mean = {mean_mv:+.2f} mV")
ax.axhline(p3sigma, color="orange", lw=1.5, linestyle="--", label=f"+3σ = {p3sigma:+.2f} mV")
ax.axhline(n3sigma, color="orange", lw=1.5, linestyle="--", label=f"−3σ = {n3sigma:+.2f} mV")
ax.set_xlabel("Run #")
ax.set_ylabel("Offset (mV)")
ax.set_title("Sorted Offset per Run")
ax.legend(fontsize=9)

plt.tight_layout()
plt.savefig("mc_offsets_plot.png", dpi=150)
print("Saved: mc_offsets_plot.png")
