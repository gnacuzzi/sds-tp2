import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
from matplotlib.patches import Circle
from itertools import product
import argparse


def read_static(path):
    with open(path, "r") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    N = int(lines[0])
    L = float(lines[1])
    rc = float(lines[2])
    v = float(lines[3])
    eta = float(lines[4])
    leader_mode = int(lines[5])

    return N, L, rc, v, eta, leader_mode


def read_dynamic(path, N):
    frames = []

    with open(path, "r") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    i = 0
    while i < len(lines):
        t = float(lines[i])
        i += 1

        data = []
        for _ in range(N):
            x, y, vx, vy, leader = lines[i].split()
            data.append([
                float(x),
                float(y),
                float(vx),
                float(vy),
                int(leader)
            ])
            i += 1

        frames.append((t, np.array(data)))

    return frames

def periodic_circle_centers(x, y, L, rc):
    centers = []
    for dx, dy in product((-L, 0, L), repeat=2):
        cx = x + dx
        cy = y + dy
        if -rc <= cx <= L + rc and -rc <= cy <= L + rc:
            centers.append((cx, cy))
    return centers


def animate(static_path, dynamic_path, interval=60, save_gif=None, show_rc=False):
    N, L, rc, v, eta, leader_mode = read_static(static_path)
    frames = read_dynamic(dynamic_path, N)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, L)
    ax.set_ylim(0, L)
    ax.set_aspect("equal")
    ax.set_box_aspect(1)
    ax.set_position([0.22, 0.12, 0.56, 0.78])
    ax.set_xlabel("x")
    ax.set_ylabel("y")

    t0, data0 = frames[0]
    x = data0[:, 0]
    y = data0[:, 1]
    vx = data0[:, 2]
    vy = data0[:, 3]
    is_leader = data0[:, 4].astype(int)

    follower_mask = is_leader == 0
    leader_mask = is_leader == 1

    follower_x = x[follower_mask]
    follower_y = y[follower_mask]
    follower_vx = vx[follower_mask]
    follower_vy = vy[follower_mask]
    follower_angles = np.arctan2(follower_vy, follower_vx)

    leader_x = x[leader_mask]
    leader_y = y[leader_mask]
    leader_vx = vx[leader_mask]
    leader_vy = vy[leader_mask]

    followers_quiver = ax.quiver(
        follower_x,
        follower_y,
        follower_vx,
        follower_vy,
        follower_angles,
        cmap="hsv",
        angles="xy",
        scale_units="xy",
        scale=0.15,
        width=0.006,
        pivot="middle"
    )

    leader_quiver = ax.quiver(
        leader_x,
        leader_y,
        leader_vx,
        leader_vy,
        color="black",
        angles="xy",
        scale_units="xy",
        scale=0.15,
        width=0.008,
        pivot="middle"
    )

    leader_circles = []
    if leader_x.size > 0:
        for cx, cy in periodic_circle_centers(leader_x[0], leader_y[0], L, rc):
            circle = Circle(
                (cx, cy),
                rc,
                fill=False,
                edgecolor="black",
                linewidth=1.2,
                alpha=0.9,
                zorder=2
            )
            ax.add_patch(circle)
            leader_circles.append(circle)
    else:
        circle = Circle(
            (0.0, 0.0),
            rc,
            fill=False,
            edgecolor="black",
            linewidth=1.2,
            alpha=0.0,
            zorder=2
        )
        ax.add_patch(circle)
        leader_circles.append(circle)

    # Círculos rc para todas las partículas (modo debug)
    rc_circles = []
    if show_rc:
        for i in range(N):
            edge = "black" if is_leader[i] == 1 else "gray"
            alpha = 0.85 if is_leader[i] == 1 else 0.18
            lw = 1.2 if is_leader[i] == 1 else 0.6

            circle = Circle(
                (x[i], y[i]),
                rc,
                fill=False,
                edgecolor=edge,
                linewidth=lw,
                alpha=alpha,
                zorder=1
            )
            ax.add_patch(circle)
            rc_circles.append(circle)

    def update(frame):
        t, data = frame

        x = data[:, 0]
        y = data[:, 1]
        vx = data[:, 2]
        vy = data[:, 3]
        is_leader = data[:, 4].astype(int)

        follower_mask = is_leader == 0
        leader_mask = is_leader == 1

        follower_x = x[follower_mask]
        follower_y = y[follower_mask]
        follower_vx = vx[follower_mask]
        follower_vy = vy[follower_mask]
        follower_angles = np.arctan2(follower_vy, follower_vx)

        leader_x = x[leader_mask]
        leader_y = y[leader_mask]
        leader_vx = vx[leader_mask]
        leader_vy = vy[leader_mask]

        followers_quiver.set_offsets(np.column_stack((follower_x, follower_y)))
        followers_quiver.set_UVC(follower_vx, follower_vy, follower_angles)

        if leader_x.size > 0:
            leader_quiver.set_offsets(np.column_stack((leader_x, leader_y)))
            leader_quiver.set_UVC(leader_vx, leader_vy)

            centers = periodic_circle_centers(leader_x[0], leader_y[0], L, rc)
            for idx, circle in enumerate(leader_circles):
                if idx < len(centers):
                    circle.center = centers[idx]
                    circle.set_radius(rc)
                    circle.set_alpha(0.9)
                else:
                    circle.center = (0.0, 0.0)
                    circle.set_alpha(0.0)
        else:
            leader_quiver.set_offsets(np.empty((0, 2)))
            leader_quiver.set_UVC(np.array([]), np.array([]))
            for circle in leader_circles:
                circle.center = (0.0, 0.0)
                circle.set_alpha(0.0)

        if show_rc:
            for i, circle in enumerate(rc_circles):
                circle.center = (x[i], y[i])
                if is_leader[i] == 1:
                    circle.set_edgecolor("black")
                    circle.set_alpha(0.85)
                    circle.set_linewidth(1.2)
                else:
                    circle.set_edgecolor("gray")
                    circle.set_alpha(0.18)
                    circle.set_linewidth(0.6)

        artists = [followers_quiver, leader_quiver]
        artists.extend(leader_circles)
        if show_rc:
            artists.extend(rc_circles)
        return artists

    anim = FuncAnimation(
        fig,
        update,
        frames=frames,
        interval=interval,
        blit=False
    )

    if save_gif is not None:
        writer = FFMpegWriter(fps=max(1, int(1000 / interval)))
        anim.save(save_gif, writer=writer)
        plt.close(fig)
    else:
        plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--static", default="output/static.txt")
    parser.add_argument("--dynamic", default="output/dynamic.txt")
    parser.add_argument("--interval", type=int, default=60)
    parser.add_argument("--save-gif", default=None)
    parser.add_argument("--show-rc", action="store_true")

    args = parser.parse_args()

    animate(
        static_path=args.static,
        dynamic_path=args.dynamic,
        interval=args.interval,
        save_gif=args.save_gif,
        show_rc=args.show_rc
    )