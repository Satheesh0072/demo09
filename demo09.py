import streamlit as st
import pandas as pd
from streamlit_chat import message
from datetime import datetime
import time

# Set up page config
st.set_page_config(page_title="Smart Restaurant Assistant", page_icon="🍽️", layout="wide")

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3075/3075977.png", width=100)
    st.title("🍔 Menu AI Assistant")
    st.markdown("Improve your restaurant performance with data insights and AI support.")
    st.markdown("---")
    st.info("Upload the latest ingredient report")

# Load and clean Excel data
@st.cache_data
def load_data():
    df = pd.read_excel("Restaurant_Google sheet001.xlsx", sheet_name="Sheet1", skiprows=3)
    df = df.dropna(subset=["Dish"])
    df.columns = df.columns.map(str)
    df["Weekly Orders"] = pd.to_numeric(df["Weekly Orders"], errors='coerce')
    df["Waste in cost"] = pd.to_numeric(df["Waste in cost"], errors='coerce')
    df["Dish Profit Margin ₹"] = pd.to_numeric(df["Dish Profit Margin ₹"], errors='coerce')
    return df

df = load_data()

st.title(":fork_and_knife: Smart Menu Optimization Assistant with AI Chatbot")

with st.expander("1. 🔎 Dishes to Remove (Low-Selling & High Waste)"):
    remove_dishes = df[(df["Weekly Orders"] < 5) & (df["Waste in cost"] > 100)]
    st.dataframe(remove_dishes[["Dish", "Weekly Orders", "Waste in cost", "Keep/Remove"]])

with st.expander("2. 🚗 Most Wasted Ingredients"):
    waste_by_ingredient = df[["Dish", "Ingredients", "Waste in cost"]].sort_values(by="Waste in cost", ascending=False)
    st.dataframe(waste_by_ingredient)

with st.expander("3. 🍝 Suggested Dish Ideas Using High-Waste Ingredients"):
    suggestions = df[df["Waste in cost"] > 100][["Dish", "Ingredients", "Waste in cost", "Suggested Dishes"]]
    st.dataframe(suggestions)

with st.expander("4. 📊 High Margin Dishes with Overlapping Ingredients"):
    margin_threshold = st.slider("Set minimum profit margin:", 50, 200, 100)
    high_margin_dishes = df[df["Dish Profit Margin ₹"] >= margin_threshold]
    st.dataframe(high_margin_dishes[["Dish", "Ingredients", "Dish Profit Margin ₹"]])

with st.expander("5. 🍏 Most Wasted Ingredient"):
    max_waste_row = df.loc[df["Waste in cost"].idxmax()]
    st.success(f"Most wasted: {max_waste_row['Ingredients']} costing ₹{max_waste_row['Waste in cost']}")

with st.expander("6. 🌱 Suggest Dish Using Existing Ingredients"):
    all_ingredients = ", ".join(df["Ingredients"].dropna().tolist())
    st.text_area("Available Ingredients (auto-filled)", value=all_ingredients, height=100)

with st.expander("7. ❌ Candidates for Removal"):
    st.dataframe(remove_dishes[["Dish", "Weekly Orders", "Waste in cost", "Keep/Remove"]])

with st.expander("8. 🚚 Suggestions to Reduce Stock Next Week"):
    to_stock_less = df[df["Weekly Orders"] < 5][["Dish", "Ingredients", "Weekly Orders"]]
    st.dataframe(to_stock_less)

col1, col2 = st.columns(2)
with col1:
    st.download_button("Download Cleaned Data 📂", data=df.to_csv(index=False), file_name="optimized_menu_data.csv", key="download_button_static")
with col2:
    st.download_button("Download Chat Insights 📂", data=df.to_csv(index=False), file_name="menu_with_chat.csv", key="download_button_chat")

st.markdown("---")
st.header(":robot_face: Chat with Menu Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

for i, msg in enumerate(st.session_state.messages):
    message(msg["content"], is_user=msg["is_user"], key=f"msg_{i}")

prompt = st.chat_input("Ask anything about dish waste, profit, or suggestions...")

def chatbot_response(user_input):
    user_input = user_input.lower()
    if "remove" in user_input or "low-selling" in user_input:
        result = df[(df["Weekly Orders"] < 5) & (df["Waste in cost"] > 100)][["Dish"]]
        return f"Remove these dishes: {', '.join(result['Dish'])}"
    elif "most wasted" in user_input or "waste" in user_input:
        max_row = df.loc[df["Waste in cost"].idxmax()]
        return f"Most wasted: {max_row['Ingredients']} in {max_row['Dish']} costing ₹{max_row['Waste in cost']}"
    elif "high margin" in user_input:
        result = df[df["Dish Profit Margin ₹"] >= 100][["Dish"]]
        return f"High margin dishes: {', '.join(result['Dish'])}"
    elif "suggest" in user_input:
        result = df[df["Waste in cost"] > 100][["Dish", "Suggested Dishes"]]
        return "Suggestions:\n" + "\n".join([f"{row['Dish']} ➔ {row['Suggested Dishes']}" for _, row in result.iterrows()])
    return "Try asking: 'most wasted', 'remove low-selling', 'high margin', or 'suggest dishes'."

if prompt:
    st.session_state.messages.append({"content": prompt, "is_user": True})
    reply = chatbot_response(prompt)
    st.session_state.messages.append({"content": reply, "is_user": False})
    message(prompt, is_user=True)
    message(reply, is_user=False)
