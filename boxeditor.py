import math

from PySide6 import QtCore, QtGui, QtWidgets


class PyOCR(QtWidgets.QApplication):
    def __init__(self, argv) -> None:
        super().__init__(argv)


class Box(QtWidgets.QGraphicsRectItem):
    def __init__(self, rect, parent=None):
        super().__init__(rect, parent)

        self.mousePressPos = None
        self.mousePressRect = None

        self.setAcceptHoverEvents(True)

        self.moving = False
        self.setFlags(QtWidgets.QGraphicsItem.ItemIsSelectable | QtWidgets.QGraphicsItem.ItemIsMovable)

    def mouseMoveEvent(self, event):
        if self.moving:
            self.prepareGeometryChange()
            pos = event.pos().toPoint()

            rect = self.rect()

            if self.left:
                rect.setLeft(pos.x())
            if self.right:
                rect.setRight(pos.x())
            if self.top:
                rect.setTop(pos.y())
            if self.bottom:
                rect.setBottom(pos.y())

            self.setRect(rect.normalized())
            self.update()
        else:
            super().mouseMoveEvent(event)

    def corner_rect(self) -> QtCore.QRectF:
        rect = self.rect()
        return QtCore.QRectF(rect.right() - 10, rect.bottom() - 10, 10, 10)

    def mousePressEvent(self, event) -> None:
        if event.buttons() == QtCore.Qt.LeftButton:
            self.origin_rect = self.rect()
            if self.left or self.right or self.top or self.bottom:
                self.moving = True
            else:
                super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        self.moving = False
        super().mouseReleaseEvent(event)

    def paint(self, painter, option, widget=None):
        brush = QtGui.QBrush(QtGui.QColor(94, 156, 235, 150))
        brush.setStyle(QtCore.Qt.SolidPattern)
        painter.setBrush(brush)
        pen = QtGui.QPen(QtGui.QColor(94, 156, 235, 0))
        pen.setStyle(QtCore.Qt.SolidLine)
        pen.setCosmetic(False)
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawRect(self.rect())

        if self.isSelected():
            pen = QtGui.QPen(QtGui.QColor(94, 156, 235, 255))
            pen.setStyle(QtCore.Qt.SolidLine)
            pen.setCosmetic(False)
            pen.setWidth(3)
            painter.setPen(pen)
            painter.setBrush(QtCore.Qt.NoBrush)
            painter.drawRect(self.rect())

        self.update()

    def hoverMoveEvent(self, event) -> None:
        self.top = False
        self.right = False
        self.bottom = False
        self.left = False

        cursor = QtGui.QCursor(QtGui.Qt.ArrowCursor)
        if math.isclose(event.pos().x(), self.rect().x(), rel_tol=0.02):
            self.left = True
        if math.isclose(event.pos().x(), self.rect().x() + self.rect().width(), rel_tol=0.02):
            self.right = True
        if math.isclose(event.pos().y(), self.rect().y(), rel_tol=0.02):
            self.top = True
        if math.isclose(event.pos().y(), self.rect().y() + self.rect().height(), rel_tol=0.02):
            self.bottom = True

        if self.top or self.bottom:
            cursor = QtGui.QCursor(QtGui.Qt.SizeVerCursor)
        if self.left or self.right:
            cursor = QtGui.QCursor(QtGui.Qt.SizeHorCursor)

        if self.top and self.right or self.bottom and self.left:
            cursor = QtGui.QCursor(QtGui.Qt.SizeBDiagCursor)
        if self.top and self.left or self.bottom and self.right:
            cursor = QtGui.QCursor(QtGui.Qt.SizeFDiagCursor)

        self.setCursor(cursor)

        super().hoverMoveEvent(event)


class BoxEditorScene(QtWidgets.QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.box = None
        self.image = QtGui.QPixmap('/mnt/Daten/Emulation/Amiga/Amiga Magazin/x-000.ppm')
        self.setSceneRect(self.image.rect())

    def mousePressEvent(self, event):
        if not self.itemAt(event.scenePos(), QtGui.QTransform()):
            if event.buttons() == QtCore.Qt.LeftButton:
                if not self.box:
                    rect = QtCore.QRectF()
                    rect.setTopLeft(event.scenePos())
                    rect.setBottomRight(event.scenePos())

                    self.box = Box(rect)
                    self.box.setSelected(True)
                    self.addItem(self.box)

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            if self.box:
                if self.box:
                    rect = self.box.rect()
                    rect.setBottomRight(event.scenePos())
                    self.box.setRect(rect)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        self.box = None
        super().mouseReleaseEvent(event)

    def drawBackground(self, painter, rect: QtCore.QRectF):
        painter.drawPixmap(self.sceneRect(), self.image, QtCore.QRectF(self.image.rect()))


class BoxEditor(QtWidgets.QGraphicsView):
    def __init__(self, parent):
        super().__init__(parent)

        self.setScene(BoxEditorScene())
