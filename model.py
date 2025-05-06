import os
import json
import numpy as np
import matplotlib.pyplot as plt
import multiprocessing
from typing import List, Tuple
from sklearn.model_selection import train_test_split

from LMDB import LMDBWrapper

# TensorFlow setup
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import tensorflow as tf
tf.get_logger().setLevel('ERROR')

from tensorflow.keras.models import Sequential  # type: ignore
from tensorflow.keras.layers import (Conv2D, MaxPooling2D, Flatten, Dense, Dropout, # type: ignore
                                     BatchNormalization, Input) 
from tensorflow.keras.utils import Sequence  # type: ignore
from tensorflow.keras.regularizers import l2  # type: ignore
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau  # type: ignore
from tensorflow.python.framework.ops import get_default_graph  # type: ignore
from tensorflow.keras.losses import Huber  # type: ignore


def fen_to_tensor(fen: str) -> np.ndarray:
    """Convert a FEN-like string to a (8, 8, 17) tensor for CNN input."""
    values = list(map(int, fen[1:-1].split(",")))
    assert len(values) == 69, f"Expected 69 values (64 board + 4 castling + 1 ep), got {len(values)}"

    board_flat = values[:64]
    castling = values[64:68]
    ep_square = values[68]

    tensor = np.zeros((8, 8, 17), dtype=np.int8)

    for i, val in enumerate(board_flat):
        if val == 0:
            continue
        plane = val - 1
        row, col = divmod(i, 8)
        tensor[row, col, plane] = 1

    for i, right in enumerate(castling):
        tensor[:, :, 12 + i] = right

    if ep_square != 0:
        row, col = divmod(ep_square, 8)
        tensor[row, col, 16] = 1

    return tensor


def read_chunk(start_idx: int, end_idx: int, db_path: str) -> Tuple[np.ndarray, np.ndarray]:
    """Worker function to read a chunk of the DB and count categories."""
    db = LMDBWrapper(db_path)
    cursor = db.env.begin().cursor()

    X_list, Y_list = [], []

    for i, (key_bytes, value_bytes) in enumerate(cursor):
        if i < start_idx:
            continue
        if i >= end_idx:
            break

        key = db._decode_key(key_bytes)
        dtype = np.dtype([('eval', np.float32), ('count', np.uint32)])
        value_array = np.frombuffer(value_bytes, dtype=dtype, count=1)
        eval_value = value_array[0]['eval']

        key_encoded = fen_to_tensor(key)
        X_list.append(key_encoded)
        Y_list.append(eval_value)

    return np.array(X_list, dtype=np.int8), np.array(Y_list, dtype=np.float32)


def load_inputs() -> Tuple[np.ndarray, np.ndarray]:
    """Load inputs from the LMDB database using multiprocessing."""
    db_path = "scoreboards"
    db = LMDBWrapper(db_path)
    # total_keys = db.count_keys()
    total_keys = 5_000_000
    num_workers = multiprocessing.cpu_count()
    chunk_size = total_keys // num_workers

    print(f"Processing {total_keys:,} entries with {num_workers} workers")

    chunks = [(i * chunk_size, (i + 1) * chunk_size if i != num_workers - 1 else total_keys)
              for i in range(num_workers)]
    args_for_workers = [(start, end, db_path) for start, end in chunks]

    with multiprocessing.Pool(num_workers) as pool:
        results = pool.starmap(read_chunk, args_for_workers)

    X = np.concatenate([result[0] for result in results], axis=0)
    y = np.concatenate([result[1] for result in results], axis=0)

    return X, y


def build_model() -> tf.keras.Model:
    """Build and return a CNN model."""
    model = Sequential([
        Input(shape=(8, 8, 17)),

        Conv2D(128, (3, 3), activation='relu', padding='same', kernel_regularizer=l2(1e-5)),
        BatchNormalization(),
        Conv2D(128, (3, 3), activation='relu', padding='same', kernel_regularizer=l2(1e-5)),
        BatchNormalization(),
        MaxPooling2D(pool_size=(2, 2)),
        Dropout(0.3),

        Conv2D(256, (3, 3), activation='relu', padding='same', kernel_regularizer=l2(1e-5)),
        BatchNormalization(),
        Conv2D(256, (3, 3), activation='relu', padding='same', kernel_regularizer=l2(1e-5)),
        BatchNormalization(),
        MaxPooling2D(pool_size=(2, 2)),
        Dropout(0.3),

        Conv2D(512, (3, 3), activation='relu', padding='same', kernel_regularizer=l2(1e-5)),
        BatchNormalization(),
        Conv2D(512, (3, 3), activation='relu', padding='same', kernel_regularizer=l2(1e-5)),
        BatchNormalization(),
        MaxPooling2D(pool_size=(2, 2)),
        Dropout(0.3),

        Flatten(),
        Dense(1024, activation='relu', kernel_regularizer=l2(1e-5)),
        BatchNormalization(),
        Dropout(0.3),

        Dense(512, activation='relu', kernel_regularizer=l2(1e-5)),
        BatchNormalization(),
        Dropout(0.3),

        Dense(1, activation='sigmoid')
    ])

    model.compile(optimizer='adam', loss=Huber(delta=1.0), metrics=['mae'])
    return model


def plot_history(history: tf.keras.callbacks.History):
    """Plot training history (loss and MAE)."""
    plt.figure(figsize=(12, 5))

    plt.subplot(1, 2, 1)
    plt.plot(history.history['loss'], label='Train Loss')
    plt.plot(history.history['val_loss'], label='Val Loss')
    plt.title('Loss Over Epochs')
    plt.xlabel('Epoch')
    plt.ylabel('MSE Loss')
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.plot(history.history['mae'], label='Train MAE')
    plt.plot(history.history['val_mae'], label='Val MAE')
    plt.title('MAE Over Epochs')
    plt.xlabel('Epoch')
    plt.ylabel('Mean Absolute Error')
    plt.legend()

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    multiprocessing.set_start_method("spawn", force=True)

    X, y = load_inputs()
    X = X.reshape((-1, 8, 8, 17))

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print(f"X shape: {X.shape}, y shape: {y.shape}")

    model = build_model()

    early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
    reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=1e-6)

    for device in tf.config.list_logical_devices():
        print(device)

    history = model.fit(
        X_train, y_train,
        validation_split=0.2,
        epochs=200,
        batch_size=512,
        verbose=1,
        callbacks=[early_stopping, reduce_lr]
    )

    test_loss, test_mae = model.evaluate(X_test, y_test)
    print(f"Test Loss: {test_loss:.4f}, Test MAE: {test_mae:.4f}")

    plot_history(history)

    with open('training_history.json', 'w') as f:
        json.dump(history.history, f)

    model.save('model.h5')
    print('Model saved successfully.')
