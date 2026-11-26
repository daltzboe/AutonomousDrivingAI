import torch
from autodrive.model import SteeringCNN

def test_model_output_is_one_normalized_steering_per_image():
    model = SteeringCNN()
    output = model(torch.zeros(2, 3, 66, 200))
    assert output.shape == (2,)
    assert torch.all(output >= -1) and torch.all(output <= 1)
