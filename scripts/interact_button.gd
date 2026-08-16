extends Button


func _ready() -> void:
	pressed.connect(func(): MobileInput.emit_interact())
