## Thoughtful Artificially intelligent and Responsive System (TARS)

The goal of this project is to develop a human-like agent using artificial intelligence. The agent will be able to communicate with the user via speech just like a normal human, solve problems and much more.
You can read more details about the vision for this project [here](Documentation/vision.md).

## Installation
1. Clone the repository.
2. Create your preferred virtual environment.
3. Go to the repository folder and run `pip install -r requirements.txt` to install all the required packages.
3. If you encounter any installation issues please make sure you have installed required libraries using following commands (on Ubuntu):
`sudo apt-get install portaudio19-dev libcairo2-dev libgirepository1.0-dev pkg-config python3-dev`
4. To use the trained models you have to retrieve them using git lfs like this: `git lfs pull`.
5. You can now run the software by running [main.py](main.py).

## Setup
1. You need to have a camera connected to your computer.
2. You need to have a microphone connected to your computer.
3. You may also want to use headphones or speakers to hear the robot's speech.
3. You may have to have a robot connected to your computer (see [here](https://www.ohbot.co.uk/store/c1/buy-ohbot)). If you don't the software will still run, you just won't be able to control the robot.
4. Many modules require OpenAI API key to function. You can get one [here](https://beta.openai.com/). This is required.

## Training
If you would like to replicate the training of the models, you can download the datasets [here](https://drive.google.com/file/d/1nj4l2pW25RxiD6ey25Xw8ZXcX6VLS_xh/view?usp=sharing).
You can run the training of the models by running `Training/Module/Aspect/trainer.py`. For example, if you would like to train the Face Recognition model,
you would run the file [Training/Vision/FaceRecognition/trainer.py](Training/Vision/FaceRecognition/trainer.py).

## Documentation
If you'd like to contribute to the project or want to learn more details about the project,
you can find more detailed documentation in the [Documentation](Documentation) folder.

Note that there may be bugs or unresolved issues in the code. If you find any, please report them in the [Issues](https://github.com/Reblexis/TARS/issues?q=is%3Aissue+is%3Aopen+sort%3Aupdated-desc) section.
