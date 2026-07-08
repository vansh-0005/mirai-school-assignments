import streamlit as st

st.title("The Identity Echo Interfac")
st.write("Enter your name and message below , then press 'TRANSMIT' to send your message")

user_name=st.text_input("Enter your name")
user_msg=st.text_input("Enter your message")

if(st.button("TRANSMIT")):
    
    if(user_name.strip()==""):
        st.error("Enter your name")
        
    elif(user_msg.strip()==""):
        st.warning("Please type a message to transmit.")
    
    else:
        st.success(
            f"Transmited sucessfully. Greeting ${user_name}"
            f"We received your msg ${user_msg}"
        )
        
        total_char=len(user_msg)
        token_used=total_char/4
        
        st.info(
            f"Your message will consume approximately"
            f"${token_used:.2f} tokens from our context window."
        )
        
