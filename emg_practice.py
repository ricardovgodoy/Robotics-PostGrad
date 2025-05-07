import pandas as pd
import numpy as np
import scipy.signal as signal
from sklearn.ensemble import RandomForestClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.metrics import confusion_matrix, accuracy_score, ConfusionMatrixDisplay
import matplotlib.pyplot as plt

# ---- CONFIGURE FILES ----
train_files = {
    'rest': ['rest1.csv', 'rest2.csv'],
    'pinch': ['pinch1.csv', 'pinch2.csv'],
    'power': ['power1.csv', 'power2.csv'],
}

test_files = {
    'rest': ['rest3.csv'],
    'pinch': ['pinch3.csv'],
    'power': ['power3.csv'],
}

# ---- PARAMETERS ----
window_ms = 200
overlap_ms = 20
sampling_rate = 1000  # Hz

window_size = int(window_ms * sampling_rate / 1000)
step_size = int((window_ms - overlap_ms) * sampling_rate / 1000)

# ---- DESIGN BANDPASS FILTER (20-450 Hz) ----
def design_bandpass_filter(lowcut, highcut, fs, order=4):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = signal.butter(order, [low, high], btype='band')
    return b, a

b, a = design_bandpass_filter(20, 450, sampling_rate)

# ---- FUNCTION TO LOAD, FILTER, WINDOW, NORMALIZE ----
def load_filter_window(files_dict, label_map):
    X = []
    Y = []

    for label_name, file_list in files_dict.items():
        label = label_map[label_name]
        for filename in file_list:
            # Load CSV
            df = pd.read_csv(filename)
            emg_signal = df['analog_value'].values

            # FILTER EMG SIGNAL
            emg_filtered = signal.filtfilt(b, a, emg_signal)

            # Sliding window
            for start_idx in range(0, len(emg_filtered) - window_size + 1, step_size):
                window = emg_filtered[start_idx:start_idx + window_size]

                # NORMALIZE WINDOW (z-score)
                window = (window - np.mean(window)) / np.std(window)

                X.append(window)
                Y.append(label)

    return np.array(X), np.array(Y)

# ---- LABELS MAP ----
label_map = {'rest': 0, 'pinch': 1, 'power': 2}

# ---- LOAD, FILTER, WINDOW, NORMALIZE DATA ----
X_train, Y_train = load_filter_window(train_files, label_map)
X_test, Y_test = load_filter_window(test_files, label_map)

print(f"X_train shape: {X_train.shape}, Y_train shape: {Y_train.shape}")
print(f"X_test shape: {X_test.shape}, Y_test shape: {Y_test.shape}")

# ---- TRAIN MODELS ----
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
lda_model = LinearDiscriminantAnalysis()

rf_model.fit(X_train, Y_train)
lda_model.fit(X_train, Y_train)

# ---- EVALUATE ----
rf_preds = rf_model.predict(X_test)
lda_preds = lda_model.predict(X_test)

rf_acc = accuracy_score(Y_test, rf_preds)
lda_acc = accuracy_score(Y_test, lda_preds)

print(f"Random Forest Accuracy: {rf_acc*100:.2f}%")
print(f"LDA Accuracy: {lda_acc*100:.2f}%")

# ---- PLOT CONFUSION MATRICES ----
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

ConfusionMatrixDisplay.from_predictions(Y_test, rf_preds, ax=axes[0], display_labels=['Rest', 'Pinch', 'Power'])
axes[0].set_title('Random Forest Confusion Matrix')

ConfusionMatrixDisplay.from_predictions(Y_test, lda_preds, ax=axes[1], display_labels=['Rest', 'Pinch', 'Power'])
axes[1].set_title('LDA Confusion Matrix')

plt.tight_layout()
plt.show()
