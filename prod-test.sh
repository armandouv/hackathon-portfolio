BASE_URL=https://armandouv.duckdns.org/
CURRENT_URL=$BASE_URL
NEW_USERNAME=$(openssl rand -base64 12)
NEW_PASSWORD=hola
red=$(tput setaf 1)
green=$(tput setaf 2)

compare_status() {
  if [ "$1" == "$2" ]; then
    echo "$green""Passed"
  else
    echo "$red""Failed"
    exit 1
  fi
  reset=$(tput sgr0)
  echo "$reset"
}

expect_get_status() {
  STATUS_CODE=$(curl -s --ignore-content --head $CURRENT_URL | head -1 | cut -d " " -f 2)
  compare_status "$1" "$STATUS_CODE"
}

expect_post_status() {
  STATUS_CODE=$(curl -w "%{http_code}" -X POST -d "$2" $CURRENT_URL -s -o /dev/null)
  compare_status "$1" "$STATUS_CODE"
}

print_url() {
  echo
  yellow=$(tput setaf 3)
  echo "${yellow}""$1"
  reset=$(tput sgr0)
  echo "$reset"
}

CURRENT_URL=$BASE_URL
print_url /
echo "Home page:"
expect_get_status 200

CURRENT_URL=${BASE_URL}gfsag
print_url /gfsag
echo "Invalid route:"
expect_get_status 404

# /profiles

CURRENT_URL=${BASE_URL}profiles/Armando
print_url /profiles/Armando
echo "Valid profile:"
expect_get_status 200

CURRENT_URL=${BASE_URL}profiles/vfdasvg
print_url /profiles/vfdasvg
echo "Invalid profile:"
expect_get_status 404

# /projects

CURRENT_URL=${BASE_URL}projects/Portfolio%20Project
print_url /projects/Portfolio%20Project
echo "Valid project:"
expect_get_status 200

CURRENT_URL=${BASE_URL}projects/vfdasvg
print_url /projects/vfdasvg
echo "Invalid project:"
expect_get_status 404

# /register

CURRENT_URL=${BASE_URL}register
print_url /register

echo "Valid registration page:"
expect_get_status 200

echo "Valid user registration:"
expect_post_status 200 "username=$NEW_USERNAME&password=hola"

echo "Invalid user registration (no username):"
expect_post_status 418 "password=$NEW_PASSWORD"

echo "Invalid user registration (no password):"
expect_post_status 418 "username=$NEW_USERNAME"

echo "Invalid user registration (username already registered):"
expect_post_status 418 "username=$NEW_USERNAME&password=$NEW_PASSWORD"

# /login

CURRENT_URL=${BASE_URL}login
print_url /login

echo "Valid login page:"
expect_get_status 200

echo "Valid user login:"
expect_post_status 200 "username=$NEW_USERNAME&password=$NEW_PASSWORD"

echo "Invalid user login (incorrect username):"
expect_post_status 418 "username=FGSFD&password=$NEW_PASSWORD"

echo "Invalid user login (incorrect password):"
expect_post_status 418 "username=$NEW_USERNAME&password=invalid"
