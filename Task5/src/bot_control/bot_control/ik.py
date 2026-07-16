#!/usr/bin/env python3
import math

D = 0.68
R = 0.14

THETA_LEFT = math.radians(90)
THETA_RIGHT = math.radians(-30)
THETA_REAR = math.radians(210)


def _wheel_speed(vx, vy, omega, theta):
    v_i = math.sin(theta) * vx - math.cos(theta) * vy - D * omega
    return v_i / R


def inverse_kinematics(vx, vy, omega):
    wl = _wheel_speed(vx, vy, omega, THETA_LEFT)
    wr = _wheel_speed(vx, vy, omega, THETA_RIGHT)
    wb = _wheel_speed(vx, vy, omega, THETA_REAR)
    return wl, wr, wb


def main():
    vx = float(input("vx (m/s): "))
    vy = float(input("vy (m/s): "))
    omega = float(input("omega (rad/s): "))

    wl, wr, wb = inverse_kinematics(vx, vy, omega)

    print(f"\nLeft wheel  : {wl:.3f} rad/s")
    print(f"Right wheel : {wr:.3f} rad/s")
    print(f"Rear wheel  : {wb:.3f} rad/s")


if __name__ == "__main__":
    main()
