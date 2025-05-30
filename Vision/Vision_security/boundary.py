from abc import ABC, abstractmethod
import winsound


class Boundary(ABC):
    @abstractmethod
    def draw_boundary(self, frame):
        pass

    @abstractmethod
    def is_crossed(self, face_coords):
        pass


# WarningManager 클래스
class WarningManager:
    def __init__(self, custom_boundary):
        self.custom_boundary = custom_boundary
        self.triggered = False

    def check_boundary(self, face_coords):
        """
        얼굴이 대각선 아래에 위치하면 확대하여 보여주는 메서드입니다.
        """
        face_coords = self._get_face_border(face_coords)
        warning = self.custom_boundary.is_crossed(face_coords)
        return warning

    @staticmethod
    def _get_face_border(face_coords):
        x, y, w, h = face_coords

        top_y = y
        bottom_y = y + h
        left_x = x
        right_x = x + w

        face_coords = (top_y, bottom_y, left_x, right_x)
        return face_coords

    @staticmethod
    def trigger_warning():
        winsound.Beep(1000, 500)