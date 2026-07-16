#!/usr/bin/env python3
import math

D = 0.68
R = 0.14


def forward_kinematics(omega_left, omega_right, omega_rear):
    v_left = omega_left * R
    v_right = omega_right * R
    v_rear = omega_rear * R

    omega = -(v_right + v_left + v_rear) / (3.0 * D)
    vx = (2.0 * v_left - v_right - v_rear) / 3.0
    vy = (v_rear - v_right) / math.sqrt(3)

    return vx, vy, omega


def main():
    wl = float(input("Left wheel (rad/s): "))
    wr = float(input("Right wheel (rad/s): "))
    wb = float(input("Rear wheel (rad/s): "))

    vx, vy, omega = forward_kinematics(
        wl,
        wr,
        wb
    )

    print(f"\nvx     : {vx:.3f} m/s")
    print(f"vy     : {vy:.3f} m/s")
    print(f"omega  : {omega:.3f} rad/s")


if __name__ == "__main__":
    main()
