import { CameraView, useCameraPermissions } from 'expo-camera';
import { useEffect, useRef, useState } from 'react';
import { Button, Dimensions, StyleSheet, Text, TouchableOpacity, View,Image } from 'react-native';
import axios from 'axios';

export default function App() {
  const [mapViewImg, setMapViewImg] = useState('');
  const [facing, setFacing] = useState('back');
  const [permission, requestPermission] = useCameraPermissions();
  const [isMobile, setIsMobile] = useState(Dimensions.get('window').width < 768);
  const cameraRef = useRef(null);
  const captureInterval = 1000; // 1s

  Dimensions.addEventListener('change', ({ window: { width } }) => {
    setIsMobile(width < 768);
  });


  useEffect(() => {
    Dimensions.addEventListener('change', ({ window: { width } }) => {
      setIsMobile(width < 768);
    });
  }, []);

  useEffect(() => {
    let interval;
    if (cameraRef.current) {
      interval = setInterval(async () => {
        if (cameraRef.current) {
          const photo = await cameraRef.current.takePictureAsync({ base64: true });
          sendImageToBackend(photo.base64);
        }
      }, captureInterval);
    }
    return () => clearInterval(interval);
  }, [cameraRef]);

  const sendImageToBackend = async (base64Image) => {
    //const url = 'http://127.0.0.1:5000/map'
    const url = 'http://127.0.0.1:5000/map'
    try {
      const response = await axios.post(url, 
        { image: base64Image },
      );
      console.log(response.status)
  
      if (response.status === 200) {
        console.log('Image uploaded successfully');
        const img = `data:image/png;base64,${response.data}`;
        setMapViewImg(img);
      } else {
        console.log(response.data);
        console.error('Failed to upload image');
      }
    } catch (error) {
      console.error('Error uploading image:', error);
    }
  };


  if (!permission) {
    // Camera permissions are still loading.
    return <View />;
  }

  if (!permission.granted) {
    // Camera permissions are not granted yet.
    return (
      <View style={styles.container}>
        <Text style={{ textAlign: 'center' }}>We need your permission to show the camera</Text>
        <Button onPress={requestPermission} title="grant permission" />
      </View>
    );
  }

  function toggleCameraFacing() {
    setFacing(current => (current === 'back' ? 'front' : 'back'));
  }

  return (
    <View style={styles.container}>
      <View style={styles.mapContainer}>
        {mapViewImg && <Image  source={{uri:mapViewImg}} style={styles.logo} /> }
      </View>
      <View style={[styles.cameraContainer, isMobile ? styles.cameraContainerMobile : styles.cameraContainerDesktop]}>
        <CameraView style={styles.camera} ref={cameraRef} facing={facing}>
          <View style={styles.buttonContainer}>
            <TouchableOpacity style={styles.button} onPress={toggleCameraFacing}>
              <Text style={styles.text}>Flip Camera</Text>
            </TouchableOpacity>
          </View>
        </CameraView>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  logo: {
    width: 500,
    height: 500,
  },
  container: {
    flex: 1,
  },
  mapContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  mapPlaceholder: {
    fontSize: 20,
    color: 'grey',
  },
  cameraContainer: {
    position: 'absolute',
    backgroundColor: 'rgba(0,0,0,0.5)',
    borderRadius: 10,
    overflow: 'hidden',
  },
  cameraContainerMobile: {
    bottom: 0,
    width: '100%',
    height: '30%',
  },
  cameraContainerDesktop: {
    right: 0,
    bottom: 0,
    width: '25%',
    height: '40%',
  },
  camera: {
    flex: 1,
  },
  buttonContainer: {
    flex: 1,
    flexDirection: 'row',
    backgroundColor: 'transparent',
    margin: 16,
  },
  button: {
    flex: 1,
    alignSelf: 'flex-end',
    alignItems: 'center',
  },
  text: {
    fontSize: 18,
    fontWeight: 'bold',
    color: 'white',
  },
});