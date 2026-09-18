"""Vector Math Toolkit: Pure Python 2D and 3D Euclidean vector algebra library.

Features operator overloading for vector arithmetic, dot product, cross product,
magnitudes, normalizations, angles, projections, and interactive calculation.
"""

import math
import sys
from typing import Tuple, Union


EPSILON = 1e-9


class Vector3D:
    """Represents a vector in 3-dimensional Euclidean space (x, y, z)."""

    def __init__(self, x: float, y: float, z: float = 0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __repr__(self) -> str:
        return f"Vector3D({self.x:g}, {self.y:g}, {self.z:g})"

    def __str__(self) -> str:
        return f"({self.x:g}, {self.y:g}, {self.z:g})"

    def __add__(self, other: "Vector3D") -> "Vector3D":
        if not isinstance(other, Vector3D):
            return NotImplemented
        return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: "Vector3D") -> "Vector3D":
        if not isinstance(other, Vector3D):
            return NotImplemented
        return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar: Union[int, float]) -> "Vector3D":
        if not isinstance(scalar, (int, float)):
            return NotImplemented
        return Vector3D(self.x * scalar, self.y * scalar, self.z * scalar)

    def __rmul__(self, scalar: Union[int, float]) -> "Vector3D":
        return self.__mul__(scalar)

    def __truediv__(self, scalar: Union[int, float]) -> "Vector3D":
        if not isinstance(scalar, (int, float)):
            return NotImplemented
        if abs(scalar) < EPSILON:
            raise ZeroDivisionError("Cannot divide vector by zero scalar.")
        return Vector3D(self.x / scalar, self.y / scalar, self.z / scalar)

    def __neg__(self) -> "Vector3D":
        return Vector3D(-self.x, -self.y, -self.z)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector3D):
            return False
        return (
            abs(self.x - other.x) < EPSILON
            and abs(self.y - other.y) < EPSILON
            and abs(self.z - other.z) < EPSILON
        )

    def magnitude(self) -> float:
        """Compute the Euclidean length (L2 norm) of the vector."""
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def magnitude_squared(self) -> float:
        """Compute squared magnitude without performing square root."""
        return self.x**2 + self.y**2 + self.z**2

    def normalized(self) -> "Vector3D":
        """Return unit vector with length 1.0 pointing in same direction."""
        mag = self.magnitude()
        if mag < EPSILON:
            raise ValueError("Cannot normalize a zero-length vector.")
        return self / mag

    def dot(self, other: "Vector3D") -> float:
        """Compute algebraic dot product between this vector and other."""
        if not isinstance(other, Vector3D):
            raise TypeError("Dot product requires another Vector3D instance.")
        return (self.x * other.x) + (self.y * other.y) + (self.z * other.z)

    def cross(self, other: "Vector3D") -> "Vector3D":
        """Compute vector cross product (self x other)."""
        if not isinstance(other, Vector3D):
            raise TypeError("Cross product requires another Vector3D instance.")
        return Vector3D(
            (self.y * other.z) - (self.z * other.y),
            (self.z * other.x) - (self.x * other.z),
            (self.x * other.y) - (self.y * other.x),
        )

    def angle_to(self, other: "Vector3D") -> Tuple[float, float]:
        """Return angle between vectors as (radians, degrees)."""
        mag_prod = self.magnitude() * other.magnitude()
        if mag_prod < EPSILON:
            raise ValueError("Cannot compute angle involving zero-length vectors.")
        cos_theta = max(-1.0, min(1.0, self.dot(other) / mag_prod))
        rad = math.acos(cos_theta)
        deg = math.degrees(rad)
        return rad, deg

    def project_onto(self, other: "Vector3D") -> "Vector3D":
        """Compute orthogonal projection of self onto other."""
        denom = other.magnitude_squared()
        if denom < EPSILON:
            raise ValueError("Cannot project onto a zero vector.")
        scalar = self.dot(other) / denom
        return other * scalar

    def distance_to(self, other: "Vector3D") -> float:
        """Compute Euclidean distance between points represented by vectors."""
        return (self - other).magnitude()


def run_tests() -> bool:
    """Verify algebraic properties and geometric formulas."""
    v1 = Vector3D(3, 4, 0)
    assert abs(v1.magnitude() - 5.0) < EPSILON

    # Normalized unit vector
    u1 = v1.normalized()
    assert abs(u1.magnitude() - 1.0) < EPSILON

    # Arithmetic
    v2 = Vector3D(1, 2, 3)
    v_add = v1 + v2
    assert v_add == Vector3D(4, 6, 3)

    v_sub = v1 - v2
    assert v_sub == Vector3D(2, 2, -3)

    v_scaled = v1 * 2
    assert v_scaled == Vector3D(6, 8, 0)

    # Dot product: orthogonal vectors have dot product 0
    vx = Vector3D(1, 0, 0)
    vy = Vector3D(0, 1, 0)
    vz = Vector3D(0, 0, 1)
    assert abs(vx.dot(vy)) < EPSILON

    # Cross product: i x j = k
    assert vx.cross(vy) == vz
    assert vy.cross(vx) == -vz

    # Angle between i and j: 90 degrees (pi / 2 radians)
    rad, deg = vx.angle_to(vy)
    assert abs(deg - 90.0) < EPSILON
    assert abs(rad - (math.pi / 2.0)) < EPSILON

    # Projection of (3, 4, 0) onto x-axis is (3, 0, 0)
    proj = v1.project_onto(vx)
    assert proj == Vector3D(3, 0, 0)

    print("All vector math toolkit test assertions passed successfully.")
    return True


def parse_vector_input(prompt_text: str) -> Optional[Vector3D]:
    """Parse comma or space separated numbers into Vector3D."""
    raw = input(prompt_text).strip()
    if not raw:
        return None
    cleaned = raw.replace(",", " ")
    parts = cleaned.split()
    try:
        if len(parts) == 2:
            return Vector3D(float(parts[0]), float(parts[1]), 0.0)
        elif len(parts) == 3:
            return Vector3D(float(parts[0]), float(parts[1]), float(parts[2]))
        else:
            print("Error: Please provide either 2 (x, y) or 3 (x, y, z) numbers.")
            return None
    except ValueError:
        print("Error: Non-numeric coordinate provided.")
        return None


def main() -> None:
    """Interactive command-line vector calculator."""
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
        return

    while True:
        print("\n================================")
        print("      Vector Math Toolkit       ")
        print("================================")
        print("1. Vector Magnitude and Normalization")
        print("2. Vector Addition and Subtraction")
        print("3. Dot Product and Angle")
        print("4. Cross Product (3D)")
        print("5. Vector Projection")
        print("6. Distance Between Points")
        print("7. Run Automated Self-Tests")
        print("8. Exit")

        choice = input("\nSelect an option (1-8): ").strip()
        if choice == "1":
            v = parse_vector_input("Enter vector coordinates (e.g. 3, 4, 0): ")
            if v:
                mag = v.magnitude()
                print(f"\nVector          : {v}")
                print(f"Magnitude       : {mag:.6f}")
                if mag > EPSILON:
                    print(f"Unit Vector     : {v.normalized()}")
                else:
                    print("Unit Vector     : Undefined for zero vector.")

        elif choice == "2":
            v1 = parse_vector_input("Enter first vector (x, y, z): ")
            v2 = parse_vector_input("Enter second vector (x, y, z): ")
            if v1 and v2:
                print(f"\nA + B = {v1 + v2}")
                print(f"A - B = {v1 - v2}")

        elif choice == "3":
            v1 = parse_vector_input("Enter first vector A (x, y, z): ")
            v2 = parse_vector_input("Enter second vector B (x, y, z): ")
            if v1 and v2:
                dot = v1.dot(v2)
                print(f"\nDot Product (A . B) : {dot:.6f}")
                try:
                    rad, deg = v1.angle_to(v2)
                    print(f"Angle Between       : {deg:.4f} degrees ({rad:.4f} rad)")
                except ValueError as err:
                    print(f"Angle Between       : {err}")

        elif choice == "4":
            v1 = parse_vector_input("Enter first vector A (x, y, z): ")
            v2 = parse_vector_input("Enter second vector B (x, y, z): ")
            if v1 and v2:
                cross = v1.cross(v2)
                print(f"\nCross Product (A x B) : {cross}")
                print(f"Magnitude of Cross    : {cross.magnitude():.6f}")

        elif choice == "5":
            v1 = parse_vector_input("Enter vector to project A (x, y, z): ")
            v2 = parse_vector_input("Enter target vector B (x, y, z): ")
            if v1 and v2:
                try:
                    proj = v1.project_onto(v2)
                    print(f"\nProjection of A onto B : {proj}")
                    print(f"Projection Magnitude   : {proj.magnitude():.6f}")
                except ValueError as err:
                    print(f"Error: {err}")

        elif choice == "6":
            v1 = parse_vector_input("Enter first point A (x, y, z): ")
            v2 = parse_vector_input("Enter second point B (x, y, z): ")
            if v1 and v2:
                dist = v1.distance_to(v2)
                print(f"\nEuclidean Distance : {dist:.6f}")

        elif choice == "7":
            run_tests()

        elif choice == "8":
            print("Exiting Vector Math Toolkit. Goodbye.")
            break
        else:
            print("Invalid option. Please choose from 1 to 8.")


if __name__ == "__main__":
    main()
