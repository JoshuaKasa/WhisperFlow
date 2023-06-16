import tkinter
import imageio
import time
import math
import os

import numpy as np

from tqdm import tqdm
from tkinter import filedialog
from PIL import Image

# Getting the binary data of a file and calculating the progression using tqdm
def get_binary_data(file_path: str) -> bytes:
    file_size = os.path.getsize(file_path)
    chunk_size = 1024  # Adjust the chunk size as per your preference

    with open(file_path, "rb") as file, tqdm(total=file_size, desc="Reading file", unit="B", unit_scale=True,
                                             bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt}") as pbar:
        binary_data = b""
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            binary_data += chunk
            pbar.update(len(chunk))

    return binary_data

# Getting the binary data from the video and calculating the progression using tqdm
def extract_binary_data_from_video(video_path: str, width: int, height: int) -> str:
    binary_data = ""
    with imageio.get_reader(video_path, mode='I') as reader, tqdm(total=reader.count_frames(),
                                                                   desc='Extracting frames',
                                                                   bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt}") as pbar:
        for frame in reader:
            image = Image.fromarray(frame)
            red_channel = image.split()[0]  # Get the red channel directly

            binary_data += "".join("1" if pixel & 0x80 else "0" for pixel in red_channel.getdata())
            pbar.update(1)

    return binary_data

def create_images_from_binary(binary_data: bytes, width: int, height: int) -> list:
    binary_string = "".join(format(c, "08b") for c in binary_data)
    num_images = math.ceil(len(binary_string) / (width * height))

    images = []

    # Use tqdm to track the progress of the loop
    with tqdm(total=num_images, desc="Creating images",
              bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt}") as pbar:
        for i in range(num_images):
            start_idx = i * (width * height)
            end_idx = start_idx + (width * height)
            image_data = binary_string[start_idx:end_idx]

            pixels = [255 if bit == "1" else 0 for bit in image_data]  # Use list comprehension for efficient pixel creation

            image = Image.new("L", (width, height))
            image.putdata(pixels)
            images.append(image)

            pbar.update(1)  # Update progress bar

    return images

def create_video(images: list, output_path: str) -> None:
    with imageio.get_writer(output_path, mode='I') as writer:
        for image in tqdm(images, desc="Creating video", bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt}"):
            frame = np.array(image)
            writer.append_data(frame)

    print("Video created successfully!")

# Convert a string of bits to bytes
def bits_to_file(binary_data: str) -> bytes:
    bytes_ = [int(binary_data[i:i+8], 2) for i in range(0, len(binary_data), 8)]
    return bytes(bytes_) # Convert the list of integers to bytes

def select_files() -> list:
    tkinter.Tk().withdraw()
    files = filedialog.askopenfilenames()
    return list(files)

def main() -> None:
    # Get the file path
    tkinter.Tk().withdraw()
    file_path = filedialog.askopenfilename()
    file_extension = file_path.split(".")[-1] # Get the file extension

    # Getting the binary data of the file
    initial_binary_data = get_binary_data(file_path)
    initial_binary_data_bits = "".join(format(c, "08b") for c in initial_binary_data) # Convert the binary data to a string of bits
    initial_binary_data_length = len(initial_binary_data_bits)

    # Specify the width and height of your images
    width = 1024
    height = 576
    images = create_images_from_binary(initial_binary_data, width, height)
    output_path = "output.mp4"

    # Creating the video
    start_time = time.time() # Start the timer
    create_video(images, output_path)
    end_time = time.time() # End the timer
    print("Video created successfully!")
    print("Time taken: {} seconds".format(end_time - start_time), "\nFor a file of size: {} bytes".format(len(initial_binary_data)))

    # Getting the binary data from the video and truncating it to the length of the initial binary data
    binary_data = extract_binary_data_from_video(output_path, width, height)
    binary_data = binary_data[:initial_binary_data_length]

    # Turning the binary data back into a file
    bytes_ = bits_to_file(binary_data) # Convert the binary data to bytes
    with open("output.{}".format(file_extension), "wb") as file:
        file.write(bytes_) # Write the bytes to the file
    print("File created successfully!")

if __name__ == "__main__":
    main()