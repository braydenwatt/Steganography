import wave

def text_to_bin(text):
    return ''.join(format(ord(c), '08b') for c in text)

def bin_to_text(binary_message):
    return ''.join(chr(int(binary_message[i:i + 8], 2)) for i in range(0, len(binary_message), 8))

def encode_audio(input_audio_path, output_audio_path, text, bit_count=1):
    audio = wave.open(input_audio_path, mode='rb')
    frame_bytes = bytearray(list(audio.readframes(audio.getnframes())))

    binary_message = text_to_bin(text)
    message_length = len(binary_message)
    binary_length = format(message_length, '032b')

    # Combine length prefix and message data
    binary_data = binary_length + binary_message
    total_bits_needed = len(binary_data)

    # Ensure there's enough space in the audio file to hold the data
    if total_bits_needed > len(frame_bytes) * bit_count:
        print("Text is too long to hide in the audio file")
        return

    clear_mask = ~((1 << bit_count) - 1)
    for i in range(total_bits_needed):
        frame_index = i // bit_count
        bit_position = i % bit_count
        frame_bytes[frame_index] &= clear_mask  # Clear bit_count LSBs
        frame_bytes[frame_index] |= int(binary_data[i]) << bit_position  # Set bit_count LSBs

    modified_audio = wave.open(output_audio_path, 'wb')
    modified_audio.setparams(audio.getparams())
    modified_audio.writeframes(bytes(frame_bytes))
    modified_audio.close()
    audio.close()
    print("Message hidden successfully!")


def decode_audio(stego_audio_path, bit_count=1):
    audio = wave.open(stego_audio_path, mode='rb')
    frame_bytes = bytearray(list(audio.readframes(audio.getnframes())))
    audio.close()

    # Extract the length of the message from the first 32 * bit_count bits
    if len(frame_bytes) < 32 * bit_count:
        print("Audio file is too short to contain message length.")
        return ""

    length_bin = ''.join(str((frame_bytes[i // bit_count] >> (i % bit_count)) & 1) for i in range(32 * bit_count))
    message_length = int(length_bin, 2)

    # Ensure we have enough data in frame_bytes to hold the full message
    total_bits_needed = message_length + 32 * bit_count
    if total_bits_needed > len(frame_bytes) * bit_count:
        print("Audio file is too short to contain the full message.")
        return ""

    # Extract the binary message based on the retrieved length
    extracted_bin = ''.join(
        str((frame_bytes[(32 * bit_count + i) // bit_count] >> (i % bit_count)) & 1)
        for i in range(message_length)
    )

    return bin_to_text(extracted_bin)


def read_text_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: The file at {file_path} does not exist.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


# Example usage
message = read_text_file('input.txt')
if message:
    encode_audio('input.wav', 'output_stego.wav', message, 3)
    hidden_message = decode_audio('output_stego.wav', 3)
    print("Original Message:", message)
    print("Retrieved Message:", hidden_message)
    print("Same?:", hidden_message == message)
