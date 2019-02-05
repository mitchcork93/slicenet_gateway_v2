# SliceNet Gateway Application

An application for the SliceNet project that could be deployed to ambulances to enable remote diagnostics by utilising 5G technology.

## Getting Started

The MEC server will need to be running before this application is launced.

### Running the program

Once all the above prerequisites are installed, navigate to the root folder of the application, then start the application.

```
python server.py
```

The application will then attempt to make a connection to the MEC server.

Upon successful connection a window will launch showing the stream from the camera, this is the patient identifier and facial recognition is used to detect
the patient and pull their patient record.

The next screen will show the patient diagnostics with AI pain detection, patient information and some dummy charts.

The pain detection will change colour depending on the severity of the pain

Green - None / little pain
Orange - Moderate pain
Red - Severe pain