# Attendance-Birthday-Tracker-Mattermost-Bot

A Python-based Mattermost bot for managing team attendance, vacations, and member information.

## Features

- Check-in and check-out functionality
- Record missing attendance
- Vacation tracking
- Team status reports
- Member management (add, update, delete, info)
- Monthly attendance reports
- Birthday reminders! :tada:

## Getting Started

### Prerequisites

- Python 3.9+
- Docker
- Mattermost server

### Running the Bot

#### Installation
1. Clone the repository:
```git
git clone https://github.com/metr0jw/Attendance-Birthday-Tracker-Mattermost-Bot && cd Attendance-Birthday-Tracker-Mattermost-Bot
```
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Set up your configuration:
- Copy `config.json.example` to `config.json`
- Edit `config.json` with your Mattermost server details and bot token

#### Using Docker

1. Build the Docker image:
```bash
docker build -t attendance-bot .
```
2. Run the Docker container:
```bash
docker run -d --name attendance-bot -v $(pwd)/config.json:/app/config.json attendance-bot
```

## Usage

All commands must start with a '!' character. Responses will be sent to Direct Message.

### Help Commands
- `!도움`, `!h`, `!help`: Show this help message

### Attendance Commands
- `!출근`, `!in`: Check in (Attend work)
- `!퇴근`, `!out`: Check out (Leave work)
- `!출퇴근누락 <date> <time_in> <time_out>`, `!missing <date> <time_in> <time_out>`: Enter missing attendance
  - Example: `!missing 2024-12-31 09:00:00 18:00:00` 
  - Example: `!출퇴근누락 2024-12-31 09:00:00 18:00:00`
- `!퇴근누락 <date> <time_out>`, `!missingout <date> <time_out>`: Enter missing leave time
  - Exmaple: `!missingout 2024-12-31 18:00` 
  - Example: `!퇴근누락 2024-12-31 18:00`
- `!휴가 <start_date> <end_date> <reason>`, `!vacation <start_date> <end_date> <reason>`: Record vacation
  - Example: `!vacation 2024-12-31 2025-01-02 Family-trip` 
  - Example: `!휴가 2024-12-31 2025-01-02 가족여행`
- `!상태 [date]`, `!teamstatus [date]`: Print all team members' statuses (optional date, defaults to current date)
  - Example: `!teamstatus 2024-12-31` 
  - Example: `!상태 2024-12-31`
- `!월간보고 [year-month]`, `!monthlyreport [year-month]`: Print the monthly attendance report (optional year-month, defaults to current month)
  - Example: `!monthlyreport 2024-12`
  - Example: `!월간보고 2024-12`

### Member Management Commands
- `!멤버추가 <@user_id> <name> <position> <phone> <email> <birthday>`, `!addmember <@user_id> <name> <position> <phone> <email> <birthday>`: Add a member
  - Example: `!addmember @gdhong Gildong_Hong PhD 010-1234-5678 gdhong@kw.ac.kr 1970-01-01` 
  - Example: `!멤버추가 @gdhong 홍길동 PhD 010-1234-5678 gdhong@kw.ac.kr 1970-01-01`
- `!멤버업데이트 <@user_id> [position] [phone] [email] [birthday]`, `!updatemember <@user_id> [position] [phone] [email] [birthday]`: Update member info (optional fields)
  - Example: `!updatemember @gdhong PhD 010-1234-5678 gdhong@kw.ac.kr 1970-01-01` 
  - Example: `!멤버업데이트 @gdhong PhD 010-1234-5678 gdhong@kw.ac.kr 1970-01-01`
- `!멤버삭제 <@user_id>`, `!deletemember <@user_id>`: Delete a member
  - Example: `!deletemember @gdhong` 
  - Example: `!멤버삭제 @gdhong`
- `!멤버조회 <@user_id>`, `!memberinfo <@user_id>`: Get member info
  - Example: `!memberinfo @gdhong` 
  - Example: `!멤버조회 @gdhong`

## Disclaimer

This project is not affiliated with Mattermost, Inc. This project is provided as-is and is not guaranteed to work in all environments.
The developer is not responsible for any data loss or damage caused by the use of this software.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Developer Information

- Developer: Jiwoon Lee (이지운)
- GitHub: [metr0jw](https://github.com/metr0jw)

Contact the developer if you have any questions or suggestions.
