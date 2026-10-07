def h2k_capacity_multiplier(t_c: float) -> float:
    return (
        0.766836
        + 0.027487 * t_c
        + 0.00028936 * t_c**2
        - 1.4658e-5 * t_c**3
        - 5.65296e-7 * t_c**4
    )


t_47f = 8.333
t_17f = -8.333
t_5f = -15.0

q47 = h2k_capacity_multiplier(t_47f)
q17 = h2k_capacity_multiplier(t_17f)
q5 = h2k_capacity_multiplier(t_5f)

print("Legacy H2K/H3K ASHP capacity curve")
print()
print(f"47F multiplier: {q47:.12f}")
print(f"17F multiplier: {q17:.12f}")
print(f"5F multiplier:  {q5:.12f}")
print()
print(f"17/47 normalized: {q17 / q47:.12f}")
print(f"5/47 normalized:  {q5 / q47:.12f}")
print()
print(
    "Canmet constant delta:",
    abs(q17 - 0.563635566),
)
