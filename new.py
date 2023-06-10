import numpy as np
from keras.models import load_model

# Load pre-trained Keras model
model = load_model('path_to_your_model.h5')

# Define the mapping of letters to indices
letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
letter_to_index = {letter: index for index, letter in enumerate(letters)}

# Define the maximum word length
max_word_length = 10

# Collect user input letters
user_input = []
while True:
    letter = input("Enter a letter (or 'q' to quit): ")
    if letter.lower() == 'q':
        break
    user_input.append(letter)

# Convert user input to numerical format
input_sequence = [letter_to_index[letter] for letter in user_input]
input_sequence = np.array(input_sequence)

# Reshape the input sequence to match the model's input shape
input_sequence = np.reshape(input_sequence, (1, len(input_sequence)))

# Generate predictions for each letter of the word
predicted_letters = []
for _ in range(max_word_length):
    predicted_sequence = model.predict(input_sequence)
    predicted_index = np.argmax(predicted_sequence)
    predicted_letter = letters[predicted_index]
    predicted_letters.append(predicted_letter)
    
    # Update the input sequence with the predicted letter index
    input_sequence = np.append(input_sequence, [[predicted_index]], axis=1)

# Display the predicted word
predicted_word = ''.join(predicted_letters)
print("Predicted word:", predicted_word)
