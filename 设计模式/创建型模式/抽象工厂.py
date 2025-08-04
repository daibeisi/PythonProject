class Button:
    def render(self):
        pass


class TextField:
    def render(self):
        pass


class WindowsButton(Button):
    def render(self):
        print("Rendering Windows button")


class WindowsTextField(TextField):
    def render(self):
        print("Rendering Windows text field")


class MacButton(Button):
    def render(self):
        print("Rendering Mac button")


class MacTextField(TextField):
    def render(self):
        print("Rendering Mac text field")


class GUIFactory:
    def create_button(self) -> Button:
        pass

    def create_text_field(self) -> TextField:
        pass


class WindowsFactory(GUIFactory):
    def create_button(self) -> Button:
        return WindowsButton()

    def create_text_field(self) -> TextField:
        return WindowsTextField()


class MacFactory(GUIFactory):
    def create_button(self) -> Button:
        return MacButton()

    def create_text_field(self) -> TextField:
        return MacTextField()


def render_ui(factory: GUIFactory):
    button = factory.create_button()
    text_field = factory.create_text_field()
    button.render()
    text_field.render()


if __name__ == "__main__":
    # 假设运行在 macOS 上
    render_ui(MacFactory())
