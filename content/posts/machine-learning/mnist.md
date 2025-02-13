---
title: "MNIST"
date: "2025-02-13"
author: "Beomsu Lee"
tags: ["machine learning", "deep learning"]
---

이미 학습된 매개변수를 사용하므로, 학습 과정은 생략하고 추론 과정만 구현할 것이다. 이 추론 과정을 신경망의 순전파(forward propagation)라고 한다.

> 신경망은 두 단계를 거쳐 문제를 해결한다. 먼저 훈련 데이터를 사용해 가중치 매개변수를 학습하고, 추론 단계에서 앞서 학습한 매개변수를 사용해 입력 데이터를 분류한다.

## MNIST 데이터셋

MNIST 데이터셋은 0부터 9까지의 숫자로 이미지로 구성된다. 훈련 이미지와 시험 이미지가 준비되어 있다.

MNIST의 이미지는 $28 \times 28$ 크기의 이미지(1채널)이며, 각 픽셀은 0~255까지의 값을 취한다. 각 이미지는 그 이미지가 실제 의미하는 숫자가 레이블로 있다.

훈련용 데이터와 테스트 데이터를 가져온다. 자세한 내용은 [여기를](https://github.com/kchcoo/WegraLee-deep-learning-from-scratch/blob/master/dataset/mnist.py) 참고하자.

```py
if __name__ == '__main__':
    (x_train, t_train), (x_test, t_test) = load_mnist(flatten=True, normalize=False)

    print(x_train.shape)
    print(t_train.shape)
    print(x_test.shape)
    print(t_test.shape)
```

`normalize`는 입력 이미지의 픽셀 값을 0.0 ~ 1.0 사이 값으로 정규화 할지 여부 파라미터다. `flatten`은 입력 이미지를 1차원 배열로 만들지를 정한다. `False`로 설정하면 입력 이미지를 $1 \times 28 \times 28$의 3차원 배열로, `True`를 설정하면 784개의 원소로 이루어진 1차원 배열로 저장한다. 

`one_hot_label`은 **원-핫 인코딩(one-hot encoding)** 형태로 저장할지를 정한다. 원-핫 인코딩은 `[0.0, 1.0, 0.0, 0.0]`처럼 정답을 뜻하는 원소만 1이고(hot), 나머지는 모두 0인 배열이다. 

```py
from PIL import Image

def img_show(img):
    pil_img = Image.fromarray(np.uint8(img))
    pil_img.show()

if __name__ == '__main__':
    (x_train, t_train), (x_test, t_test) = load_mnist(flatten=True, normalize=False)

    img = x_train[0]
    label = t_train[0]
    print(label)

    print(img.shape)
    img = img.reshape(28, 28) # 원래 이미지의 모양으로 변형
    print(img.shape)

    img_show(img)
```

## 신경망 추론

입력층 뉴런을 784개, 출력층 뉴런을 10개로 구성한다. 은닉층은 총 두 개로, 첫 번째 은닉층에는 50개의 뉴런을, 두 번째 은닉층에는 100개의 뉴런을 배치한다.

```py
def get_data():
    (x_train, t_train), (x_test, t_test) = load_mnist(normalize=True, flatten=True, one_hot_label=False)
    return x_test, t_test

def init_network():
    with open("sample_weight.pkl", 'rb') as f:
        network = pickle.load(f)
    return network

def predict(network, x):
    W1, W2, W3 = network['W1'], network['W2'], network['W3']
    b1, b2, b3 = network['b1'], network['b2'], network['b3']

    a1 = np.dot(x, W1) + b1
    z1 = sigmoid(a1)
    a2 = np.dot(z1, W2) + b2
    z2 = sigmoid(a2)
    a3 = np.dot(z2, W3) + b3
    y = softmax(a3)

    return y
```

위 신경망 추론을 수행해보고, 정확도(accuracy)를 평가해보자.

```py
if __name__ == '__main__':
    x, t = get_data()
    network = init_network()
    accuracy_cnt = 0
    for i in range(len(x)):
        y = predict(network, x[i])
        p = np.argmax(y)  # 확률이 가장 높은 원소의 인덱스를 얻는다.
        if p == t[i]:
            accuracy_cnt += 1

    print("Accuracy:" + str(float(accuracy_cnt) / len(x)))
```

```
Accuracy:0.9352
```

`predict()` 함수는 각 레이블의 확률을 넘파이 배열로 반환한다. 그 다음 `np.argmax()` 함수로 이 배열에서 값이 가장 큰 원소의 인덱스를 구한다.

데이터를 특정 범위로 변환하는 처리를 **정규화(normalization)** 이라 하고, 신경망의 데이터에 특정 변환을 가하는 것을 **전처리(pre-processing)** 이라 한다.

이외에도 전체 평균과 표준편차를 이용해 데이터들이 0을 중심으로 분포하도록 이동하거나, 데이터의 확산 범위를 제한하거나, 전체 데이터를 균일하게 분포시키는 백색화(whitening) 등의 기법도 있다.

## 배치 처리

가중치 매개변수를 확인해보자.

```py
if __name__ == '__main__':
    x, t = get_data()
    network = init_network()
    W1, W2, W3 = network['W1'], network['W2'], network['W3']

    print(x[0].shape)

    print(W1.shape)
    print(W2.shape)
    print(W3.shape)
```

```py
(784,)
(784, 50)
(50, 100)
(100, 10)
```

이미지 데이터 1장을 입력했을 때 다음과 같이 처리된다.

$$
784 \rightarrow 784 \times 50 \rightarrow 50 \times 100 \rightarrow 100 \times 10 \rightarrow 10
$$

그렇다면 이미지를 여러 장(100장)을 입력하는 경우를 생각해보자.

$$
100 \times 784 \rightarrow 784 \times 50 \rightarrow 50 \times 100 \rightarrow 100 \times 10 \rightarrow 10
$$

입력 데이터 형상은 $100 \times 784$, 출력 데이터 형상은 $100 \times 10$이 된다. 이는 100장 분량 입력 데이터의 결과가 한 번에 출력됨을 나타낸다. 즉, `x[0]`과 `y[0]`에 0번째 이미지와 그 추론 결과가, `x[1]`과 `y[1]`에는 1번째 이미지와 그 추론 결과가 저장되는 식이다.

이렇게 하나로 묶은 입력 데이터를 **배치(batch)** 라 한다. 배치로 처리할 때 다음과 같은 이점이 있다.

1. 수치 계산 라이브러리 대부분이 큰 배열을 효율적으로 처리할 수 있도록 최적화되어 있다.
2. 배치 처리로 버스에 주는 부하를 줄일 수 있다. 즉, 느린 I/O를 통해 데이터를 읽는 횟수가 줄어 빠른 CPU나 GPU 순수 계산을 수행하는 비율이 높아진다.

```py
if __name__ == '__main__':
    x, t = get_data()
    network = init_network()

    batch_size = 100 # 배치 추가
    accuracy_cnt = 0
    
    for i in range(0, len(x), batch_size):
        x_batch = x[i:i + batch_size]
        y_batch = predict(network, x_batch)
        p = np.argmax(y_batch, axis=1) # 1번째 차원을 축으로 최댓값의 인덱스를 구함
        accuracy_cnt += np.sum(p == t[i:i + batch_size])

    print("Accuracy:" + str(float(accuracy_cnt) / len(x)))
```