from math import sqrt, inf



class AToBConstAccel:
    """\
The model of movement from A to B.
The speed at point A and B is 0.
The rates of acceleration and deceleration
are constant."""
    def __init__(self, dist, accel, decel, max_speed=inf):
        """\
dist:      The distance between A to B;
accel:     The rate of acceleration;
decel:     The rate of deceleration;
max_speed: Optional. The max speed of movement."""
        self.dist = dist
        self.accel = accel
        self.decel = decel
        d0 = dist * decel / (accel + decel)
        d1 = 0
        t0 = sqrt(2*d0/accel)
        t1 = 0
        t2 = accel / decel * t0
        vc = accel * t0
        if vc > max_speed:
            t0 = max_speed / accel
            t2 = max_speed / decel
            d0 = max_speed * t0 / 2
            d1 = dist - 0.5*(accel*t0*t0 + decel*t2*t2)
            t1 = d1 / max_speed
            vc = max_speed
        self.t0 = t0
        self.t1 = t1
        self.t2 = t2
        self.T0 = t0
        self.T1 = t0 + t1
        self.T2 = t0 + t1 + t2
        self.d0 = d0
        self.d1 = d1
        self.d0_d1 = d0 + d1
        self.vc = vc


    def get_pos(self, t):
        """\
Calculating the current position with respect to t (time).
t:      the current time;
Return: the distance to A.
"""
        t0 = self.t0
        T0, T1, T2 = self.T0, self.T1, self.T2
        d0, d0_d1 = self.d0, self.d0_d1
        accel, decel = self.accel, self.decel
        vc = self.vc
        if t <= T0:
            return accel*t*t/2
        elif T0 < t <= T1:
            return d0 + (t - t0)*vc
        elif T1 < t <= T2:
            return d0_d1 + ((T2-t)*decel + vc) * (t - T1) / 2
        else:
            return self.dist
