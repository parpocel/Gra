extends Label


func _ready() -> void:
	visible = not DisplayServer.is_touchscreen_available()


func _process(_delta: float) -> void:
	if visible and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
		visible = false
