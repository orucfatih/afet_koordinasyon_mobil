import { StyleSheet, Text, View, ActivityIndicator, Pressable, Dimensions } from 'react-native'
import React from 'react'
import * as Animatable from 'react-native-animatable'
import Ionicons from 'react-native-vector-icons/Ionicons'

const { width, height } = Dimensions.get('window')

const Loading = (props) => {
  return (
    <Animatable.View 
      animation="fadeIn" 
      duration={300}
      style={styles.container}
    >
      {/* Background Overlay */}
      <View style={styles.overlay} />
      
      {/* Close Button */}
      {props.changeIsLoading && (
        <Pressable 
          onPress={() => props.changeIsLoading()}
          style={styles.closeButtonContainer}
          android_ripple={{ color: 'rgba(255,255,255,0.3)', borderless: true }}
        >
          <Ionicons name="close" size={20} color="white" />
        </Pressable>
      )}
      
      {/* Loading Content */}
      <Animatable.View 
        animation="zoomIn" 
        duration={500} 
        delay={200}
        style={styles.loadingContent}
      >
        {/* Modern Loading Circle */}
        <View style={styles.loadingCircle}>
          <Animatable.View 
            animation="rotate" 
            iterationCount="infinite" 
            duration={1500}
            style={styles.spinnerContainer}
          >
            <View style={styles.spinner} />
          </Animatable.View>
          
          {/* Inner Content */}
          <View style={styles.innerContent}>
            <View style={styles.logoContainer}>
              <Ionicons name="shield-checkmark" size={32} color="#D32F2F" />
            </View>
          </View>
        </View>
        
        {/* Loading Text */}
        <Animatable.Text 
          animation="fadeInUp" 
          delay={400}
          style={styles.loadingText}
        >
          Yükleniyor
        </Animatable.Text>
        
        {/* Subtitle */}
        <Animatable.Text 
          animation="fadeInUp" 
          delay={600}
          style={styles.loadingSubtitle}
        >
          Lütfen bekleyin...
        </Animatable.Text>

        {/* Progress Dots */}
        <Animatable.View 
          animation="fadeInUp" 
          delay={800}
          style={styles.progressDots}
        >
          <Animatable.View 
            animation="pulse" 
            iterationCount="infinite" 
            duration={1000}
            style={[styles.dot, styles.dot1]} 
          />
          <Animatable.View 
            animation="pulse" 
            iterationCount="infinite" 
            duration={1000}
            delay={200}
            style={[styles.dot, styles.dot2]} 
          />
          <Animatable.View 
            animation="pulse" 
            iterationCount="infinite" 
            duration={1000}
            delay={400}
            style={[styles.dot, styles.dot3]} 
          />
        </Animatable.View>
      </Animatable.View>
    </Animatable.View>
  )
}

export default Loading

const styles = StyleSheet.create({
    container:{
        width:"100%",
        height:"100%",
        position:"absolute",
        alignItems:"center",
        justifyContent:"center",
        backgroundColor:"white",
    },

    loadingTextStyle: {
        fontWeight:"bold"
    },
    closeButton:{
        color:"black",
        fontWeight:"bold",
        textAlign:"center",
    },
    closeButtonContainer:{
        backgroundColor:"lightgray",
        width:"30",
        height:"30",
        borderRadius:30,
        alignItems:"center",
        justifyContent:"center",
        position:"absolute",
        top:"50",
        right:"15",
    },
    overlay: {
        position: 'absolute',
        width: '100%',
        height: '100%',
        backgroundColor: 'rgba(26, 26, 26, 0.95)',
        backdropFilter: 'blur(10px)',
    },
    loadingContent: {
        alignItems: 'center',
        justifyContent: 'center',
    },
    loadingCircle: {
        width: 120,
        height: 120,
        borderRadius: 60,
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        alignItems: 'center',
        justifyContent: 'center',
        marginBottom: 30,
        shadowColor: '#D32F2F',
        shadowOffset: { width: 0, height: 8 },
        shadowOpacity: 0.3,
        shadowRadius: 20,
        elevation: 15,
        position: 'relative',
    },
    spinnerContainer: {
        position: 'absolute',
        width: 140,
        height: 140,
        borderRadius: 70,
    },
    spinner: {
        width: 140,
        height: 140,
        borderRadius: 70,
        borderWidth: 3,
        borderColor: 'transparent',
        borderTopColor: '#D32F2F',
        borderRightColor: '#D32F2F',
    },
    innerContent: {
        alignItems: 'center',
        justifyContent: 'center',
    },
    logoContainer: {
        backgroundColor: 'rgba(211, 47, 47, 0.1)',
        padding: 12,
        borderRadius: 20,
    },
    loadingText: {
        fontSize: 24,
        fontWeight: 'bold',
        color: 'white',
        marginBottom: 8,
        textShadowColor: 'rgba(0, 0, 0, 0.3)',
        textShadowOffset: { width: 0, height: 2 },
        textShadowRadius: 4,
    },
    loadingSubtitle: {
        fontSize: 16,
        color: 'rgba(255, 255, 255, 0.8)',
        marginBottom: 30,
    },
    progressDots: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 8,
    },
    dot: {
        width: 8,
        height: 8,
        borderRadius: 4,
        backgroundColor: '#D32F2F',
    },
    dot1: {
        backgroundColor: '#D32F2F',
    },
    dot2: {
        backgroundColor: '#2196F3',
    },
    dot3: {
        backgroundColor: '#4CAF50',
    },
})