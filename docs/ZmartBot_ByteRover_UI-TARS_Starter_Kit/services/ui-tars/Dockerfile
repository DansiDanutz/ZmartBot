# Use Playwright base if you prefer custom image; compose uses official image
FROM mcr.microsoft.com/playwright:v1.47.0-jammy
WORKDIR /app
COPY tasks ./tasks
RUN npm init -y && npm install playwright
CMD ["bash", "-lc", "node tasks/run.js"]
