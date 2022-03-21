import torch
from torch import nn

from .teacher_model import TeacherModel
from .vit_student import VitStudent


class ModelImageDistilled(nn.Module):
    def __init__(self, teacher_name, input_resolution, patch_size, width, layers, heads, output_dim):
        super(ModelImageDistilled, self).__init__()
        self.teacher = TeacherModel(teacher_name=teacher_name)
        for p in self.parameters():
            p.requires_grad = False

        self.student = VitStudent(input_resolution, patch_size, width, layers, heads, output_dim)

    def forward(self, image):
        stu_encode = self.student.forward(image)
        with torch.no_grad():
            tea_encode = self.teacher.encode_image(image).float()
        return stu_encode, tea_encode
