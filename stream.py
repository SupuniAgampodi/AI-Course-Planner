import streamlit as st
import subprocess
import json


# Loading Json file based on the course code entered

def load_course_data(course_code):
    file_path = f'{course_code}.json'
    with open(file_path, 'r') as f:
        return json.load(f)

# Define custom CSS styles with background image and additional styling
page_by_img = """
<style>
[data-testid="stAppViewContainer"]
{
    background-image: url("https://upload.wikimedia.org/wikipedia/commons/b/b2/A_black_background.jpg?20170209161534");
    background-size: cover;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

.content {
    padding: 20px;
    color: White;
    position: relative;
    z-index: 1;
    text-align: center;
}

.title {
    font-size: 36px;
    color: white;
    margin-bottom: 30px;
}

.logo {
    position: absolute;
    top: 10px;
    right: 10px;
    width: 100px;
    height: auto;
}

.text-input {
    background-color: rgba(255, 255, 255, 0.5);
    border: none;
    border-radius: 12px;
    padding: 15px 20px;
    margin-bottom: 20px;
    color: black;
}

.text-input:focus {
    outline: none;
    box-shadow: 0 0 0 3px rgba(70, 130, 180, 0.5);
}

.tile-container {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    margin-top: 20px;
}

.checkbox-container {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    align-items: center;
}
</style>
"""

st.markdown(page_by_img, unsafe_allow_html=True)


# Adding user selected electives to the main json data

def Add_Electives_Todata(data, electives):
    for elective in electives:
        data['units'][elective] = data['electives'][elective]
        data['units'][elective]['type'] = 'elective'
    return data

# Function is called when  user press "generate schedule" button

def Run(course_code, electives):
    data = load_course_data(course_code)
    data_with_electives = Add_Electives_Todata(data, electives)
    
    with open('modified_data.json', 'w') as f:
        json.dump(data_with_electives, f)
    print(data)

    try:
        output = subprocess.check_output(['python', 'Course_Planner.py', course_code, 'modified_data.json']).decode('utf-8')
        
        specific_lines = [line for line in output.split('\n') if "Best individual:" in line or "Best fitness:" in line or line.startswith("Semester")]
        
        for line in specific_lines:
            st.text(line)
    except subprocess.CalledProcessError as e:
        st.error(f'Error: {e.output.decode("utf-8")}')

######## Main Function ##########

def main():
    st.markdown('<div class="content">', unsafe_allow_html=True)
    st.image("https://seekvectorlogo.com/wp-content/uploads/2021/11/murdoch-university-vector-logo-small.png", width=100)
    st.markdown('<h1 class="title">Course Scheduler</h1>', unsafe_allow_html=True)

    course_code = st.text_input('Enter the desired course code:', value='', max_chars=10, key='course_code', help='Enter course code here')

    if course_code: 

##################### Code if Course code is = "MJ-ICSN"  #######################

        if course_code=='MJ-ICSN': # for CYBER MAJOR
            
            data = load_course_data(course_code)
            elective_options = data['electives']

            if 'selected_electives' not in st.session_state:
                st.session_state.selected_electives = []

            st.markdown('<div class="checkbox-container">', unsafe_allow_html=True)
            selected_electives = {'odd': [], 'even': []}
            odd_col, even_col = st.columns(2) 
            

            for idx, elective in enumerate(elective_options):
                semester = elective_options[elective]['available']
                if semester[0]==1:
                    with odd_col:
                        if st.checkbox(elective, key=elective):
                            selected_electives['odd'].append(elective)

                elif semester[0]==2:
                    with even_col:
                        if st.checkbox(elective, key=elective):
                            selected_electives['even'].append(elective)


                    # Ensure constraints
                    if len(selected_electives['odd']) > 1:
                        st.warning('You can only select one "semester 1" elective.')
                        selected_electives['odd'].pop()
                    if len(selected_electives['even']) > 2:
                        st.warning('You can only select up to two semester 2 electives.')
                        selected_electives['even'].pop()

            st.markdown('</div>', unsafe_allow_html=True)

            total_credits_odd = sum(elective_options[ele]['credits'] for ele in selected_electives['odd'])
            total_credits_even = sum(elective_options[ele]['credits'] for ele in selected_electives['even'])
            total_credits = total_credits_odd + total_credits_even
            if st.button('Generate Schedule') and total_credits==6:
               Run(course_code, selected_electives['odd'] + selected_electives['even'])
                
                
            else:
                st.warning('Total credits must be exactly 6.')



######################## Code FOR RUNNING THE DATA SCIENCE MAJOR ############################
        else:  
               
            data = load_course_data(course_code)
            elective_options = list(data['electives'].keys())

            if 'selected_electives' not in st.session_state:
                st.session_state.selected_electives = []

            st.markdown('<div class="checkbox-container">', unsafe_allow_html=True)
            selected_electives = []
            cols = st.columns(3)  # Display 3 units per line
            
            for idx, elective in enumerate(elective_options):
                col = cols[idx % 3]
                with col:
                    if st.checkbox(elective, key=elective):
                        selected_electives.append(elective)
                    if len(selected_electives) > 2:
                        st.warning('You can only select two electives.')
                        selected_electives.pop()

            total_credits = sum(data['electives'][elective]['credits'] for elective in selected_electives)

            if st.button('Generate Schedule') and total_credits == 6 :
                Run(course_code, selected_electives)
            elif total_credits != 6:
                st.warning('Total credits must be exactly 6, You can either do ICT621 or Select other two Electives.')

    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == '__main__':
    main()
