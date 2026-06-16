plugins {
    id("com.android.application")
    id("kotlin-android")
    // El plugin de Flutter DEBE estar aquí
    id("dev.flutter.flutter-gradle-plugin")
}

android {
    namespace = "com.example.aurora_mobile"

    // Versiones alineadas
    compileSdk = 35
    defaultConfig {
        applicationId = "com.example.aurora_mobile"
        minSdk = 23
        targetSdk = 35
        versionCode = flutter.versionCode
        versionName = flutter.versionName
    }

    // Forzamos el NDK que piden tus plugins
    ndkVersion = "27.0.12077973"

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }
    kotlinOptions {
        jvmTarget = JavaVersion.VERSION_11.toString()
    }

    buildTypes {
        release {
            // Firma de debug para facilitar pruebas
            signingConfig = signingConfigs.getByName("debug")
        }
        debug {
            // Cleartext va en el Manifest de debug (no aquí)
        }
    }
}

// Este bloque también es obligatorio para Flutter
flutter {
    source = "../.."
}
