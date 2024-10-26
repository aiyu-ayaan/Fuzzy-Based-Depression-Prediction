import streamlit as st
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import plotly.graph_objects as go


def create_depression_risk_system():
    """Creates the fuzzy logic system for depression risk assessment"""
    # Input variables
    mood = ctrl.Antecedent(np.arange(0, 11, 1), 'mood')
    energy = ctrl.Antecedent(np.arange(0, 11, 1), 'energy')
    appetite = ctrl.Antecedent(np.arange(-5, 6, 1), 'appetite')
    social = ctrl.Antecedent(np.arange(0, 11, 1), 'social')

    # Output variable
    risk = ctrl.Consequent(np.arange(0, 101, 1), 'risk')

    # Membership functions
    mood['low'] = fuzz.trimf(mood.universe, [0, 0, 5])
    mood['medium'] = fuzz.trimf(mood.universe, [3, 5, 7])
    mood['high'] = fuzz.trimf(mood.universe, [5, 10, 10])

    energy['low'] = fuzz.trimf(energy.universe, [0, 0, 5])
    energy['medium'] = fuzz.trimf(energy.universe, [3, 5, 7])
    energy['high'] = fuzz.trimf(energy.universe, [5, 10, 10])

    appetite['decreased'] = fuzz.trimf(appetite.universe, [-5, -5, 0])
    appetite['normal'] = fuzz.trimf(appetite.universe, [-2, 0, 2])
    appetite['increased'] = fuzz.trimf(appetite.universe, [0, 5, 5])

    social['low'] = fuzz.trimf(social.universe, [0, 0, 5])
    social['medium'] = fuzz.trimf(social.universe, [3, 5, 7])
    social['high'] = fuzz.trimf(social.universe, [5, 10, 10])

    risk['low'] = fuzz.trimf(risk.universe, [0, 0, 40])
    risk['medium'] = fuzz.trimf(risk.universe, [30, 50, 70])
    risk['high'] = fuzz.trimf(risk.universe, [60, 100, 100])

    # Rule base
    rule1 = ctrl.Rule(mood['low'] & energy['low'] & social['low'], risk['high'])
    rule2 = ctrl.Rule(mood['low'] & energy['low'] & appetite['decreased'], risk['high'])
    rule3 = ctrl.Rule(mood['medium'] & energy['medium'] & social['medium'], risk['medium'])
    rule4 = ctrl.Rule(mood['high'] & energy['high'] & social['high'], risk['low'])
    rule5 = ctrl.Rule(mood['low'] & social['low'], risk['high'])
    rule6 = ctrl.Rule(energy['low'] & appetite['decreased'], risk['high'])
    rule7 = ctrl.Rule(mood['medium'] & energy['medium'] & appetite['normal'], risk['medium'])
    rule8 = ctrl.Rule(social['medium'] & appetite['normal'] & mood['medium'], risk['medium'])
    rule9 = ctrl.Rule(mood['high'] & energy['medium'] & social['medium'], risk['low'])

    # Create control system
    depression_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5,
                                          rule6, rule7, rule8, rule9])
    return ctrl.ControlSystemSimulation(depression_ctrl)


def create_gauge_chart(risk_score):
    """Creates a gauge chart to visualize the risk score"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "black"},
            'steps': [
                {'range': [0, 40], 'color': "lightgreen"},
                {'range': [40, 70], 'color': "yellow"},
                {'range': [70, 100], 'color': "salmon"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': risk_score
            }
        }
    ))

    fig.update_layout(
        title={'text': "Depression Risk Assessment", 'y': 0.9},
        margin=dict(l=20, r=20, t=50, b=20),
        height=300
    )
    return fig


def main():
    st.set_page_config(page_title="Depression Risk Assessment", layout="wide")

    # Title and description
    st.title("Depression Risk Assessment System")
    st.markdown("""
    This tool uses fuzzy logic to assess depression risk based on multiple factors.
    Please note that this is for educational purposes only and should not be used as a diagnostic tool.
    Always consult with mental health professionals for proper evaluation and diagnosis.
    """)

    # Create two columns for layout
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Input Parameters")

        # Input sliders
        mood = st.slider(
            "Mood Level (0: Very Low, 10: Very High)",
            0, 10, 5,
            help="Rate your overall mood over the past two weeks"
        )

        energy = st.slider(
            "Energy Level (0: Very Low, 10: Very High)",
            0, 10, 5,
            help="Rate your energy level over the past two weeks"
        )

        appetite = st.slider(
            "Appetite Changes (-5: Decreased, 0: Normal, 5: Increased)",
            -5, 5, 0,
            help="Rate your appetite changes over the past two weeks"
        )

        social = st.slider(
            "Social Activity (0: Very Withdrawn, 10: Very Social)",
            0, 10, 5,
            help="Rate your level of social interaction over the past two weeks"
        )

    # Create fuzzy logic system
    try:
        depression_sim = create_depression_risk_system()

        # Input values
        depression_sim.input['mood'] = mood
        depression_sim.input['energy'] = energy
        depression_sim.input['appetite'] = appetite
        depression_sim.input['social'] = social

        # Compute result
        depression_sim.compute()
        risk_score = float(depression_sim.output['risk'])

        # Determine risk category
        if risk_score < 40:
            risk_category = "Low"
            color = "green"
        elif risk_score < 70:
            risk_category = "Medium"
            color = "orange"
        else:
            risk_category = "High"
            color = "red"

        with col2:
            st.subheader("Assessment Results")

            # Display gauge chart
            fig = create_gauge_chart(risk_score)
            st.plotly_chart(fig, use_container_width=True)

            # Display risk category
            st.markdown(f"""
            ### Risk Category: <span style='color:{color}'>{risk_category}</span>
            Risk Score: {risk_score:.1f}/100
            """, unsafe_allow_html=True)

            # Recommendations based on risk level
            st.subheader("Recommendations")
            if risk_category == "Low":
                st.markdown("""
                - Continue maintaining your current healthy habits
                - Practice regular self-care and stress management
                - Stay connected with your support network
                """)
            elif risk_category == "Medium":
                st.markdown("""
                - Consider consulting with a mental health professional
                - Increase physical activity and social interactions
                - Practice stress-reduction techniques
                - Maintain a regular sleep schedule
                """)
            else:
                st.markdown("""
                - **Strongly recommended** to seek professional help
                - Contact a mental health professional or counselor
                - Reach out to trusted friends or family members
                - Consider calling a mental health helpline
                - Maintain regular contact with healthcare providers
                """)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.markdown("Please try adjusting the input values or refresh the page.")


if __name__ == "__main__":
    main()