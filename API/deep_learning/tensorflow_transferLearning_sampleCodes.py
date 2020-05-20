
# 샘플 / https://www.mlq.ai/transfer-learning-tensorflow-2-0/

def sample_one():
    base_model = tf.keras.applications.ResNet50(weights='imagenet', include_top = False)
    x = base_model.output
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dense(1024, activation='relu')(x)
    x = tf.keras.layers.Dense(1024, activation='relu')(x)
    x = tf.keras.layers.Dense(1024, activation='relu')(x)
    x = tf.keras.layers.Dense(512, activation='relu')(x)
    preds = tf.keras.layers.Dense(2, activation ='softmax')(x)

    model = tf.keras.models.Model(inputs=base_model.input, outputs=preds)
    for layer in model.layers[:175]:
        layer.trainable = False
    for layer in model.layers[175:]:
        layer.trainable = True

    train_datagen = tf.keras.preprocessing.image.ImageDataGenerator(preprocessing_function=tf.keras.applications.resnet50.preprocess_input)
    train_generator = train_datagen.flow_from_directory('/content/drive/My Drive/Colab Notebooks/TF 2.0 Advanced/Transfer Learning Data/train/', 
                                                       target_size = (224, 224),
                                                       color_mode = 'rgb',
                                                       batch_size = 32,
                                                       class_mode = 'categorical',
                                                       shuffle = True)

    model.compile(optimizer='Adam', loss='categorical_crossentropy', metrics=['accuracy'])
    history = model.fit_generator(generator = train_generator, steps_per_epoch=train_generator.n//train_generator.batch_size, epochs = 5)

    Sample_Image = tf.keras.preprocessing.image.img_to_array(Sample_Image)
    Sample_Image = np.expand_dims(Sample_Image, axis = 0)
    Sample_Image = tf.keras.applications.resnet50.preprocess_input(Sample_Image)
    predictions = model.predict(Sample_Image)
    print('Predictions:', predictions)

# 샘플 / https://towardsdatascience.com/transfer-learning-with-tf-2-0-ff960901046d

def sample_two():
    NCLASSES = 2
    HEIGHT = 224
    WIDTH = 224
    NUM_CHANNELS = 3
    BATCH_SIZE = 32

    base_model = tf.keras.applications.vgg19.VGG19(input_shape=(HEIGHT, WIDTH, NUM_CHANNELS), include_top=False, weights='imagenet')
    base_model.trainable = False

    x = base_model.output
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dense(4096, activation='relu')(x)
    x = layers.Dense(1, activation='sigmoid')(x)
    model = models.Model(inputs=base_model.input, outputs=x)

            def preprocess_image(image):
              image = tf.image.decode_jpeg(image, channels=NUM_CHANNELS)
              image = tf.image.resize(image, [HEIGHT, WIDTH])
              image /= 255.0  # normalize to [0,1] range
              return image

            def load_and_preprocess_image(path):
              image = tf.io.read_file(path)
              return preprocess_image(image)

            path_ds = tf.data.Dataset.from_tensor_slices(files)
            image_ds = path_ds.map(load_and_preprocess_image, num_parallel_calls=AUTOTUNE)
            label_ds = tf.data.Dataset.from_tensor_slices(tf.cast(categories, tf.int64))
            image_label_ds = tf.data.Dataset.zip((image_ds, label_ds))
            ds = image_label_ds.shuffle(buffer_size=1000 * BATCH_SIZE)
            ds = ds.repeat()
            ds = ds.batch(BATCH_SIZE)
            # `prefetch` lets the dataset fetch batches, in the background while the model is training.
            ds = ds.prefetch(buffer_size=AUTOTUNE)

    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    model.fit(ds, epochs=3, steps_per_epoch=10)

# 샘플 / https://adventuresinmachinelearning.com/transfer-learning-tensorflow-2/

def sample_three():
    import tensorflow as tf
    from tensorflow.keras import layers
    import tensorflow_datasets as tfds
    split = (80, 10, 10)
    splits = tfds.Split.TRAIN.subsplit(weighted=split)
    (cat_train, cat_valid, cat_test), info = tfds.load(
        'cats_vs_dogs', split=list(splits), with_info=True, as_supervised=True)

    IMAGE_SIZE = 100
    def pre_process_image(image, label):
        image = tf.cast(image, tf.float32)
        image = image / 255.0
        image = tf.image.resize(image, (IMAGE_SIZE, IMAGE_SIZE))
        return image, label

    TRAIN_BATCH_SIZE = 64
    cat_train = cat_train.map(pre_process_image).shuffle(1000).repeat().batch(TRAIN_BATCH_SIZE)
    cat_valid = cat_valid.map(pre_process_image).repeat().batch(1000)

    IMG_SHAPE = (IMAGE_SIZE, IMAGE_SIZE, 3)
    res_net = tf.keras.applications.ResNet50(weights='imagenet', include_top=False, input_shape=IMG_SHAPE)
    res_net.trainable = False

    global_average_layer = layers.GlobalAveragePooling2D()
    output_layer = layers.Dense(1, activation='sigmoid')
    tl_model = tf.keras.Sequential([
        res_net,
        global_average_layer,
        output_layer
        ])

    tl_model.compile(optimizer=tf.keras.optimizers.Adam(),
                    loss='binary_crossentropy',
                    metrics=['accuracy'])

    callbacks = [tf.keras.callbacks.TensorBoard(log_dir='./log/transer_learning_model', update_freq='batch')]

    tl_model.fit(cat_train, steps_per_epoch = 23262//TRAIN_BATCH_SIZE, epochs=7, 
                validation_data=cat_valid, validation_steps=10, callbacks=callbacks)


# 샘플 / https://lambdalabs.com/blog/tensorflow-2-0-tutorial-02-transfer-learning/
# 데이터를 CSV로 넘기려는 경우


# 샘플 / https://rubikscode.net/2019/11/11/transfer-learning-with-tensorflow-2/
# 전이학습위한 클래스 만들기 예시 >> Wrapper(call) / DataLoader

"""
tf.data.Dataset 이점
- 간단하고 효율이 높은 데이터 파이프라인 작성 가능
- 텐서플로 입력 파이프라인 빌드 가이드: https://www.tensorflow.org/guide/data

(예시 - 판다스 데이터프레임)
dataset = tf.data.Dataset.from_tensor_slices((df.values, target.values))

"""
