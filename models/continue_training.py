import sys
sys.path.append("/workspaces/webpage_categorization")

import tensorflow as tf
import tensorflow_text as text
import keras
from datetime import datetime
from bert_preprocessing import preprocess_for_NER
from losses import CustomNonPaddingTokenLoss
from metrics import custom_accuracy, entities_only_accuracy
from keras.callbacks import ModelCheckpoint, EarlyStopping
from models.datasets.tweebank_ner.loader import TweebankNERLoader
from models.datasets.BTC.loader import BTCLoader


if __name__ == "__main__":
    ds = TweebankNERLoader().load('train').apply(preprocess_for_NER).batch(64).shuffle(64).prefetch(tf.data.experimental.AUTOTUNE)
    ds_dev = TweebankNERLoader().load('val').apply(preprocess_for_NER).batch(64).prefetch(tf.data.experimental.AUTOTUNE)

    path = "/workspaces/webpage_categorization/models/checkpoints/my_ner_model_bert_lstm_20230219_125757"
    model_checkpoint_name = path.split("/")[-1]
    # load model
    with keras.utils.custom_object_scope({'CustomNonPaddingTokenLoss': CustomNonPaddingTokenLoss,
                                          'custom_accuracy': custom_accuracy,
                                          'entities_only_accuracy': entities_only_accuracy}):
        model = tf.keras.models.load_model(path)



    # create a custom loss function
    loss_fn = CustomNonPaddingTokenLoss()

    # define callbacks
    checkpoint = ModelCheckpoint("/workspaces/webpage_categorization/models/tmp/checkpoint/checkpoint", save_weights_only=True, monitor='val_loss', verbose=1, save_best_only=True, mode='min')
    early = EarlyStopping(monitor="val_loss", mode="min", patience=5)

    # train the model
    history = model.fit(ds, epochs=10, validation_data=ds_dev, callbacks=[early, checkpoint])

    # print the history
    print(history.history)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    model.save(f"/workspaces/webpage_categorization/models/checkpoints/{model_checkpoint_name}_{timestamp}")
    print(f"Model saved to /workspaces/webpage_categorization/models/checkpoints/{model_checkpoint_name}_{timestamp}.")

    # evaluate the model
    ds = TweebankNERLoader().load('test').apply(preprocess_for_NER).batch(64).prefetch(tf.data.experimental.AUTOTUNE)

    with keras.utils.custom_object_scope({'CustomNonPaddingTokenLoss': CustomNonPaddingTokenLoss,
                                          'custom_accuracy': custom_accuracy,
                                          'entities_only_accuracy': entities_only_accuracy}):
        model = tf.keras.models.load_model(f"/workspaces/webpage_categorization/models/checkpoints/{model_checkpoint_name}_{timestamp}")
    model.evaluate(ds)
