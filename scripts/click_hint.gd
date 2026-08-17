extends Label

const AUTO_HIDE_AFTER := 6.0

var _age := 0.0


func _process(delta: float) -> void:
	if not visible:
		return
	if Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
		visible = false
		return
	_age += delta
	if _age > AUTO_HIDE_AFTER:
		visible = false
