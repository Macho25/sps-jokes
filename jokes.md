## invert mouse button1 and button2
gsettings set org.gnome.desktop.peripherals.mouse left-handed true

## some notifications
notify-send "System Error" "Critical kernel module failure detected" notify-send -u critical "WARNING" "Unauthorized keyboard activity detected"

## cursor size
gsettings set org.gnome.desktop.interface cursor-size 128

## slower animations
gsettings set org.gnome.desktop.interface enable-animations true
gsettings set org.gnome.desktop.interface gtk-enable-primary-paste false

## set wallpaper
gsettings set org.gnome.desktop.background picture-uri "file:///home/USER/Pictures/troll.jpg" 

## blink
gsettings set org.gnome.desktop.interface cursor-blink true
gsettings set org.gnome.desktop.interface cursor-blink-time 300

## inverted scrool
gsettings set org.gnome.desktop.peripherals.mouse natural-scroll true


## delay of the keyboard
gsettings reset org.gnome.desktop.peripherals.keyboard delay


## should talk?
spd-say "Hello. I am inside the machine."

## reset back to normal
dconf reset -f /org/gnome/



