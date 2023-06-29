FROM golang:1.19
WORKDIR /go/src/app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN go build -o /go/bin/app
EXPOSE 8080
CMD ["/go/bin/app"]
