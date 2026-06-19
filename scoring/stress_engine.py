class StressEngine:

    def __init__(self):
        pass

    def calculate(self, metrics):

        keyboard = metrics["keyboard"]
        mouse = metrics["mouse"]
        window = metrics["window"]
        session = metrics["session"]

        # -------------------------
        # Individual Contributors
        # -------------------------

        typing_score = (
            min(keyboard["backspaces_per_min"] * 2, 25)
            +
            min(keyboard["typing_variance"] * 10, 25)
            +
            min(keyboard["avg_pause"] * 5, 20)
        )

        context_score = min(
            window["window_switches"] * 5,
            20
        )

        mouse_score = min(
            mouse["click_rate"] * 1.5,
            20
        )

        fatigue_score = min(
            session["session_minutes"] / 5,
            20
        )

        stress_score = round(
            min(
                typing_score
                + context_score
                + mouse_score
                + fatigue_score,
                100
            ),
            2
        )

        # -------------------------
        # Classification
        # -------------------------

        if stress_score <= 25:
            level = "Relaxed"

        elif stress_score <= 50:
            level = "Mild Stress"

        elif stress_score <= 75:
            level = "High Stress"

        else:
            level = "Critical Stress"

        # -------------------------
        # Recommendation
        # -------------------------

        recommendation = {
            "title": "Keep Working",
            "reason": "Stress levels are normal."
        }

        if fatigue_score > 15:

            recommendation = {
                "title": "Take a Break",
                "reason": "Long continuous work session detected."
            }

        elif context_score > 15:

            recommendation = {
                "title": "Reduce Context Switching",
                "reason": "Frequent application switching detected."
            }

        elif typing_score > 20:

            recommendation = {
                "title": "Slow Down",
                "reason": "Typing behavior suggests frustration."
            }

        return {

            "stress": {
                "score": stress_score,
                "level": level
            },

            "contributors": {
                "typing": round(typing_score, 2),
                "context_switching": round(context_score, 2),
                "mouse_activity": round(mouse_score, 2),
                "fatigue": round(fatigue_score, 2)
            },

            "recommendation": recommendation
        }