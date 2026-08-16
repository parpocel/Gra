# Gra — low-poly gra przygodowa (Godot 4)

Szkielet projektu w Godot 4.3, gotowy pod eksport na iPhone i Androida.
Sterowanie działa zarówno na klawiaturze/myszy (testy w edytorze), jak
i dotykiem (wirtualny joystick + przeciąganie po ekranie do rozglądania się).

## Struktura projektu

```
scenes/World.tscn      – główna scena: podłoże, światło, gracz, UI
scenes/Player.tscn      – postać gracza (CharacterBody3D) + kamera trzecioosobowa
scripts/player.gd       – ruch, obrót, sterowanie kamerą
scripts/mobile_input.gd – autoload zbierający input z dotyku i przekazujący go do gracza
scripts/touch_joystick.gd, look_zone.gd, interact_button.gd – logika UI dotykowego
ui/TouchControls.tscn   – nakładka z joystickiem, strefą rozglądania i przyciskiem interakcji
assets/models/          – tu trafiają eksporty z Blendera (.glb)
assets/textures/        – tekstury (jeśli nie są wbudowane w .glb)
assets/materials/       – materiały Godota (jeśli chcesz nadpisać te z Blendera)
```

Gracz ma pod spodem `ModelRoot` (pusty `Node3D`) — tam podłącza się/instancjuje
docelowy model postaci z Blendera zamiast tymczasowej niebieskiej kapsuły.

## Jak dostarczać modele z Blendera

1. W Blenderze: **File → Export → glTF 2.0 (.glb)**.
2. Zaznacz „+Y Up”, zastosuj wszystkie transformacje (Object → Apply → All
   Transforms) przed eksportem, żeby uniknąć złej skali/rotacji w Godocie.
3. Trzymaj się low-poly (rozsądna liczba trójkątów, tekstury do 1–2K) —
   to ważne pod kątem wydajności na telefonach.
4. Wrzuć plik `.glb` do `assets/models/`. Godot automatycznie go zaimportuje
   jako scenę — możesz go przeciągnąć jako dziecko `ModelRoot` w `Player.tscn`
   albo instancjonować osobno dla elementów otoczenia w `World.tscn`.

## Uruchamianie i testy

Wymagany [Godot 4.3+](https://godotengine.org/download) (edytor).
Otwórz folder projektu w Godocie i uruchom scenę `scenes/World.tscn`.

- Klawiatura: WASD — ruch, mysz — rozglądanie (ESC zwalnia kursor), E — interakcja.
- Na telefonie/w podglądzie dotykowym: joystick w lewym dolnym rogu — ruch,
  przeciąganie prawą częścią ekranu — kamera, przycisk „Interact” — interakcja.

## Eksport na iOS i Androida

Eksport wymaga dodatkowej konfiguracji poza tym repozytorium (certyfikaty,
konta deweloperskie) — nie trzymamy tu `export_presets.cfg`, bo zawiera dane
specyficzne dla maszyny/dewelopera.

**Android:**
1. Zainstaluj Android SDK + skonfiguruj go w Godocie (Editor → Editor Settings → Export → Android).
2. `Project → Export → Add... → Android`, ustaw pakiet (np. `com.twojafirma.gra`).
3. Do publikacji w Google Play potrzebny keystore i jednorazowa opłata za konto dewelopera.

**iOS:**
1. Eksport wymaga macOS + Xcode (Godot generuje projekt Xcode, który trzeba zbudować/podpisać na Macu).
2. Potrzebne płatne konto Apple Developer (99 USD/rok) do podpisywania i publikacji.
3. `Project → Export → Add... → iOS`, potem otwórz wygenerowany projekt w Xcode.

Na start, do szybkich testów na obu platformach bez App Store, można też
używać **Godot Remote Debug** (uruchamianie buildu deweloperskiego
bezpośrednio z edytora na podłączonym telefonie) albo eksportować grę do
web/WASM jako alternatywną ścieżkę udostępniania.

## Co dalej

- Podmienić placeholdery (niebieska kapsuła gracza, zielona płyta podłoża)
  na modele z Blendera.
- Rozbudować `scripts/player.gd` o system dialogów/questów zgodnie z pomysłem na rozgrywkę.
- Dodać dźwięk, animacje (Godot AnimationPlayer/AnimationTree) i UI menu.
