# dinnerBooker
Book dinner at www.chuiyanxiaochu.com for Chen. Writen in Python 3.x

### Booking
- By sending POST request with data {did, teamid, token, name}
- Auto-select dish based upon the order of preference list. (one at the top is the favorite)
- Record new dishes
  * The new dishes names would be added into preference file starting with '# '
  * User could include new dishes by removing '# ' and re-rank them

### Notification by terminal-notifier
- Which dish is booked
- New dishes in todays menu when they are not in preference list
- Error message if failed
