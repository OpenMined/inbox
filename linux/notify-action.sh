#!/usr/bin/env bash

DBUS_MONITOR_PID=/tmp/notify-action-dbus-monitor.$$.pid
DBUS_MONITOR=(dbus-monitor --session "type='signal',interface='org.freedesktop.Notifications'")

NOTIFICATION_ID="$1"
if [[ -z "$NOTIFICATION_ID" ]]; then
    exit 1
fi
shift

ACTION_COMMANDS=("$@")
if [[ -z "$ACTION_COMMANDS" ]]; then
    exit 1
fi

cleanup() {
    rm -f "$DBUS_MONITOR_PID"
}

create_pid_file() {
    rm -f "$DBUS_MONITOR_PID"
    umask 077
    touch "$DBUS_MONITOR_PID"
}

invoke_action() {
    local invoked_action_id="$1"
    local action="" cmd=""

    for index in "${!ACTION_COMMANDS[@]}"; do
        if [[ $((index % 2)) == 0 ]]; then
            action="${ACTION_COMMANDS[$index]}"
        else
            cmd="${ACTION_COMMANDS[$index]}"
            if [[ "$action" == "$invoked_action_id" ]]; then
                bash -c "${cmd}" &
                return
            fi
        fi
    done
}

monitor() {
    create_pid_file
    
    ( "${DBUS_MONITOR[@]}" & echo $! >&3 ) 3>"$DBUS_MONITOR_PID" | while read -r line; do
        # Handle notification closed signal
        if [[ "$line" =~ "member=NotificationClosed" ]]; then
            read -r line  # notification ID
            closed_notification_id=$(echo "$line" | sed 's/^.*uint32 \([0-9]\+\).*$/\1/')
            
            if [[ "$closed_notification_id" == "$NOTIFICATION_ID" ]]; then
                invoke_action close
                break
            fi
            
        # Handle action invoked signal
        elif [[ "$line" =~ "member=ActionInvoked" ]]; then
            read -r line  # notification ID
            invoked_id=$(echo "$line" | sed 's/^.*uint32 \([0-9]\+\).*$/\1/')
            read -r line  # action ID
            action_id=$(echo "$line" | sed 's/^.*string "\(.*\)".*$/\1/')
            
            if [[ "$invoked_id" == "$NOTIFICATION_ID" ]]; then
                invoke_action "$action_id"
                break
            fi
        fi
    done
    kill $(<"$DBUS_MONITOR_PID")
    cleanup
}

trap 'cleanup; exit' INT TERM

monitor