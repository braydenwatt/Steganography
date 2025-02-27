from PIL import Image

def hide_message(image_path, message, output_path):
    # Open the input image
    img = Image.open(image_path)
    img = img.convert('RGB')
    pixels = img.load()

    # Convert the message to binary
    binary_message = ''.join([format(ord(char), '08b') for char in message])
    message_length = len(binary_message)
    binary_length = format(message_length, '032b')  # 32 bits to store the length

    # Combine length and message binary
    binary_data = binary_length + binary_message

    # Embed the data in the least significant bit of each pixel color component
    idx = 0
    for y in range(img.height):
        for x in range(img.width):
            if idx < len(binary_data):
                r, g, b = pixels[x, y]
                r = (r & ~1) | int(binary_data[idx]) if idx < len(binary_data) else r
                g = (g & ~1) | int(binary_data[idx + 1]) if idx + 1 < len(binary_data) else g
                b = (b & ~1) | int(binary_data[idx + 2]) if idx + 2 < len(binary_data) else b
                pixels[x, y] = (r, g, b)
                idx += 3
            else:
                break
        if idx >= len(binary_data):
            break

    # Save the image with the hidden message
    img.save(output_path)
    print(f"Message hidden in image saved as {output_path}")

def retrieve_message(image_path):
    # Open the steganographed image
    img = Image.open(image_path)
    img = img.convert('RGB')
    pixels = img.load()

    binary_data = ''
    for y in range(img.height):
        for x in range(img.width):
            r, g, b = pixels[x, y]
            binary_data += str(r & 1)
            binary_data += str(g & 1)
            binary_data += str(b & 1)

    # Read the first 32 bits to get the length of the message
    binary_length = binary_data[:32]
    message_length = int(binary_length, 2)

    # Extract the message bits based on the length
    binary_message = binary_data[32:32 + message_length]

    # Convert binary message to text
    chars = [binary_message[i:i + 8] for i in range(0, len(binary_message), 8)]
    message = ''.join([chr(int(char, 2)) for char in chars if len(char) == 8])

    return message

# Example usage:
image_path = 'original.jpg'
output_path = 'output_image_with_hidden_message.png'
message = 'Hello World'

# Hide the message
hide_message(image_path, message, output_path)

# Retrieve the message
hidden_message = retrieve_message(output_path)
print("Hidden message:", hidden_message)
