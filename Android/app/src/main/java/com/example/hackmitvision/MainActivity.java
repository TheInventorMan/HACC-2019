package com.example.hackmitvision;


import android.Manifest;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.media.AudioFormat;
import android.media.AudioRecord;
import android.media.MediaPlayer;
import android.media.MediaRecorder;
import android.net.Uri;
import android.net.http.AndroidHttpClient;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import java.text.SimpleDateFormat;
import java.util.Date;

import android.util.Log;
import android.view.KeyEvent;
import android.view.View;
import android.widget.Button;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.FileProvider;

import org.apache.http.HttpResponse;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.FileEntity;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.net.URI;
import java.security.AllPermission;

public class MainActivity extends AppCompatActivity {

    public class WavRecorder {
        private static final int RECORDER_BPP = 16;
        private static final String AUDIO_RECORDER_FOLDER = "AudioRecorder";
        private static final String AUDIO_RECORDER_TEMP_FILE = "record_temp.raw";
        private static final int RECORDER_SAMPLERATE = 44100;
        private static final int RECORDER_CHANNELS = AudioFormat.CHANNEL_IN_MONO;
        private static final int RECORDER_AUDIO_ENCODING = AudioFormat.ENCODING_PCM_16BIT;
        short[] audioData;

        private AudioRecord recorder = null;
        private int bufferSize = 0;
        private Thread recordingThread = null;
        private boolean isRecording = false;
        int[] bufferData;
        int bytesRecorded;

        private String output;

        public WavRecorder(String path) {
            bufferSize = AudioRecord.getMinBufferSize(RECORDER_SAMPLERATE,
                    RECORDER_CHANNELS, RECORDER_AUDIO_ENCODING) * 3;

            audioData = new short[bufferSize]; // short array that pcm data is put
            // into.
            output = path;

        }

        private String getFilename() {
            return (output);
        }

        private String getTempFilename() {
            String filepath = Environment.getExternalStorageDirectory().getPath();
            File file = new File(filepath, AUDIO_RECORDER_FOLDER);

            if (!file.exists()) {
                file.mkdirs();
            }

            File tempFile = new File(filepath, AUDIO_RECORDER_TEMP_FILE);

            if (tempFile.exists())
                tempFile.delete();

            return (file.getAbsolutePath() + "/" + AUDIO_RECORDER_TEMP_FILE);
        }

        public void startRecording() {

            recorder = new AudioRecord(MediaRecorder.AudioSource.MIC,
                    RECORDER_SAMPLERATE, RECORDER_CHANNELS,
                    RECORDER_AUDIO_ENCODING, bufferSize);
            int i = recorder.getState();
            if (i == 1)
                recorder.startRecording();

            isRecording = true;

            recordingThread = new Thread(new Runnable() {
                @Override
                public void run() {
                    writeAudioDataToFile();
                }
            }, "AudioRecorder Thread");
            Toast.makeText(getApplicationContext(), "Playing started", Toast.LENGTH_LONG).show();
            recordingThread.start();
        }

        private void writeAudioDataToFile() {
            byte data[] = new byte[bufferSize];
            String filename = getTempFilename();
            FileOutputStream os = null;

            try {
                os = new FileOutputStream(filename);
            } catch (FileNotFoundException e) {
                e.printStackTrace();
            }

            int read = 0;
            if (null != os) {
                while (isRecording) {
                    read = recorder.read(data, 0, bufferSize);
                    if (read > 0) {
                    }

                    if (AudioRecord.ERROR_INVALID_OPERATION != read) {
                        try {
                            os.write(data);
                        } catch (IOException e) {
                            e.printStackTrace();
                        }
                    }
                }

                try {
                    os.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }

        public void stopRecording() {
            if (null != recorder) {
                isRecording = false;

                int i = recorder.getState();
                if (i == 1)
                    recorder.stop();
                recorder.release();

                recorder = null;
                recordingThread = null;

                Toast.makeText(getApplicationContext(), "Image Saved", Toast.LENGTH_LONG).show();
            }

            copyWaveFile(getTempFilename(), getFilename());
            deleteTempFile();
        }

        private void deleteTempFile() {
            File file = new File(getTempFilename());
            file.delete();
        }

        private void copyWaveFile(String inFilename, String outFilename) {
            FileInputStream in = null;
            FileOutputStream out = null;
            long totalAudioLen = 0;
            long totalDataLen = totalAudioLen + 36;
            long longSampleRate = RECORDER_SAMPLERATE;
            int channels = ((RECORDER_CHANNELS == AudioFormat.CHANNEL_IN_MONO) ? 1
                    : 2);
            long byteRate = RECORDER_BPP * RECORDER_SAMPLERATE * channels / 8;

            byte[] data = new byte[bufferSize];

            try {
                in = new FileInputStream(inFilename);
                out = new FileOutputStream(outFilename);
                totalAudioLen = in.getChannel().size();
                totalDataLen = totalAudioLen + 36;

                WriteWaveFileHeader(out, totalAudioLen, totalDataLen,
                        longSampleRate, channels, byteRate);

                while (in.read(data) != -1) {
                    out.write(data);
                }

                in.close();
                out.close();
            } catch (FileNotFoundException e) {
                e.printStackTrace();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }

        private void WriteWaveFileHeader(FileOutputStream out, long totalAudioLen,
                                         long totalDataLen, long longSampleRate, int channels, long byteRate)
                throws IOException {
            byte[] header = new byte[44];

            header[0] = 'R'; // RIFF/WAVE header
            header[1] = 'I';
            header[2] = 'F';
            header[3] = 'F';
            header[4] = (byte) (totalDataLen & 0xff);
            header[5] = (byte) ((totalDataLen >> 8) & 0xff);
            header[6] = (byte) ((totalDataLen >> 16) & 0xff);
            header[7] = (byte) ((totalDataLen >> 24) & 0xff);
            header[8] = 'W';
            header[9] = 'A';
            header[10] = 'V';
            header[11] = 'E';
            header[12] = 'f'; // 'fmt ' chunk
            header[13] = 'm';
            header[14] = 't';
            header[15] = ' ';
            header[16] = 16; // 4 bytes: size of 'fmt ' chunk
            header[17] = 0;
            header[18] = 0;
            header[19] = 0;
            header[20] = 1; // format = 1
            header[21] = 0;
            header[22] = (byte) channels;
            header[23] = 0;
            header[24] = (byte) (longSampleRate & 0xff);
            header[25] = (byte) ((longSampleRate >> 8) & 0xff);
            header[26] = (byte) ((longSampleRate >> 16) & 0xff);
            header[27] = (byte) ((longSampleRate >> 24) & 0xff);
            header[28] = (byte) (byteRate & 0xff);
            header[29] = (byte) ((byteRate >> 8) & 0xff);
            header[30] = (byte) ((byteRate >> 16) & 0xff);
            header[31] = (byte) ((byteRate >> 24) & 0xff);
            header[32] = (byte) (((RECORDER_CHANNELS == AudioFormat.CHANNEL_IN_MONO) ? 1
                    : 2) * 16 / 8); // block align
            header[33] = 0;
            header[34] = RECORDER_BPP; // bits per sample
            header[35] = 0;
            header[36] = 'd';
            header[37] = 'a';
            header[38] = 't';
            header[39] = 'a';
            header[40] = (byte) (totalAudioLen & 0xff);
            header[41] = (byte) ((totalAudioLen >> 8) & 0xff);
            header[42] = (byte) ((totalAudioLen >> 16) & 0xff);
            header[43] = (byte) ((totalAudioLen >> 24) & 0xff);

            out.write(header, 0, 44);
        }
    }

    private static final String LOG_TAG = "AudioRecordTest";
    private static final int ALL_PERMISSIONS = 101;
    private static String fileName = null;

    private Button recordButton = null;
    private WavRecorder recorder = null;

    private boolean mStartRecording = true;

    // Requesting permission to RECORD_AUDIO
    private boolean permissionToRecordAccepted = false;
    private String [] permissions = {Manifest.permission.RECORD_AUDIO, Manifest.permission.CAMERA, Manifest.permission.WRITE_EXTERNAL_STORAGE, Manifest.permission.READ_EXTERNAL_STORAGE};

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        switch (requestCode){
            case ALL_PERMISSIONS:
                permissionToRecordAccepted  = grantResults[0] == PackageManager.PERMISSION_GRANTED;
                break;
        }
        if (!permissionToRecordAccepted ) finish();

    }

    private void onRecord(boolean start) {
        if (start) {
            startRecording();
        } else {
            stopRecording();
            captureImage();
        }
    }

    private void startRecording() {
        String filepath = Environment.getExternalStorageDirectory().getPath();
        File file = new File(filepath, "AudioRecorder");
        recorder = new WavRecorder(file.getAbsolutePath() + "/" + "audio.wav");
        recorder.startRecording();
    }

    private void stopRecording() {
        recorder.stopRecording();
        recorder = null;
    }

    public void onCreate(Bundle savedBundleInstance) {
        super.onCreate(savedBundleInstance);
        setContentView(R.layout.activity_main);


        // Record to the external cache directory for visibility
//        fileName = getExternalCacheDir().getAbsolutePath();
//        fileName += "/audiorecordtest.3gp";

        ActivityCompat.requestPermissions(this, permissions, ALL_PERMISSIONS);

        recordButton = findViewById(R.id.recordButton);

        recordButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                onRecord(mStartRecording);
                if (mStartRecording) {
                    recordButton.setText("Stop recording");
                } else {
                    recordButton.setText("Start recording");
                }
                mStartRecording = !mStartRecording;
            }
        });

    }

    @Override
    public void onStop() {
        super.onStop();
        if (recorder != null) {
            recorder.stopRecording();
            recorder = null;
        }
    }

    String currentPhotoPath;

    private File createImageFile() throws IOException {
        // Create an image file name
        String imageFileName = "capturedImage";
        String filepath = Environment.getExternalStorageDirectory().getPath();
        File storageDir = new File(filepath, "AudioRecorder");
        File image = File.createTempFile(
                imageFileName,  /* prefix */
                ".jpg",         /* suffix */
                storageDir      /* directory */
        );

        // Save a file: path for use with ACTION_VIEW intents
        currentPhotoPath = image.getAbsolutePath();
        return image;
    }

    public void captureImage() {
        Intent takePictureIntent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
        // Ensure that there's a camera activity to handle the intent
        if (takePictureIntent.resolveActivity(getPackageManager()) != null) {
            // Create the File where the photo should go
            File photoFile = null;
            try {
                photoFile = createImageFile();
            } catch (IOException ex) {
                ex.getStackTrace();
            }
            // Continue only if the File was successfully created
            if (photoFile != null) {
                Uri photoURI = FileProvider.getUriForFile(this,
                        "com.example.android.fileprovider",
                        photoFile);
                takePictureIntent.putExtra(MediaStore.EXTRA_OUTPUT, photoURI);
                startActivityForResult(takePictureIntent, ALL_PERMISSIONS);

                HttpClient http = AndroidHttpClient.newInstance("MyApp");
                HttpPost method = new HttpPost("http://url-to-server");
                method.setEntity(new FileEntity(new File("path-to-file"), "application/octet-stream"));
                HttpResponse response = http.execute(method);

                HttpPost method = new HttpPost("http://url-to-server");
                method.setEntity(new FileEntity(new File("path-to-file"), "application/octet-stream"));
                HttpResponse response = http.execute(method);

            }
        }
    }

    public void playAudio(){
        String filepath = Environment.getExternalStorageDirectory().getPath();
        File file = new File(filepath, "AudioRecorder");
        MediaPlayer mp = MediaPlayer.create(getApplicationContext(), R.raw.audio);
        mp.start();
        mp.release();
    }
//    @Override
//    public boolean onKeyDown(int keyCode, KeyEvent event) {
//        if ((keyCode == KeyEvent.KEYCODE_VOLUME_DOWN)){
//            captureImage();
//        }
//        return true;
//    }
}
