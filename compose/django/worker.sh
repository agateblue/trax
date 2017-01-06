sigint_handler()
{
  kill $PID
  exit
}

trap sigint_handler SIGINT
CMD="python /app/manage.py trax_schedule"
while true; do
  $CMD &
  PID=$!
  inotifywait -r -e close_write /app/
  kill $PID
done
