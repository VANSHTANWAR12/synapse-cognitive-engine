class StressEngine:

    def __init__(self):
        pass

    def calculate(self, metrics):

        keyboard = metrics["keyboard"]
        mouse = metrics["mouse"]
        window = metrics["window"]
        session = metrics["session"]

        stress_score = 0

        # --------------------
        # Typing Stress
        # --------------------

        stress_score += min(
            keyboard["backspaces_per_min"] * 2,
            25
        )

        stress_score += min(
            keyboard["typing_variance"] * 10,
            25
        )

        stress_score += min(
            keyboard["avg_pause"] * 5,
            20
        )

        # --------------------
        # Context Switching
        # --------------------

        stress_score += min(
            window["window_switches"] * 5,
            20
        )

        # --------------------
        # Mouse Frustration
        # --------------------

        stress_score += min(
            mouse["click_rate"] * 1.5,
            20
        )

        # --------------------
        # Fatigue
        # --------------------

        stress_score += min(
            session["session_minutes"] / 5,
            20
        )

        stress_score = round(
            min(stress_score, 100),
            2
        )

        # --------------------
        # Classification
        # --------------------

        if stress_score <= 25:
            level = "Relaxed"

        elif stress_score <= 50:
            level = "Mild Stress"

        elif stress_score <= 75:
            level = "High Stress"

        else:
            level = "Critical Stress"

        return {
            "stress_score": stress_score,
            "stress_level": level
        }