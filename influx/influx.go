package influx

import (
	"context"
	"time"

	influxdb2 "github.com/influxdata/influxdb-client-go/v2"
	"github.com/influxdata/influxdb-client-go/v2/api"
	log "github.com/sirupsen/logrus"
)

type Influx struct {
	client   influxdb2.Client
	writeAPI api.WriteAPIBlocking
	queryAPI api.QueryAPI
}

const (
	org    = "my-org"
	bucket = "my-bucket"
)

func NewInflux() *Influx {
	client := influxdb2.NewClient("http://influxdb:8086", "my-super-secret-auth-token")
	writeAPI := client.WriteAPIBlocking(org, bucket)
	queryAPI := client.QueryAPI(org)
	return &Influx{client, writeAPI, queryAPI}
}

// func (i *Influx) Write(ctx context.Context, data []byte) error {
// 	// write data to influx
// 	p := influxdb2.NewPoint("stat",
// 		map[string]string{"unit": "temperature"},
// 		map[string]interface{}{"avg": 24.6, "max": 45.0},
// 		time.Now())
// 	err := i.writeAPI.WritePoint(ctx, p)
// 	if err != nil {
// 		return err
// 	}
// 	return nil
// }

func (i *Influx) InsertUptime(ctx context.Context, job_id string, success bool) error {
	// write data to influx
	p := influxdb2.NewPoint("uptime",
		map[string]string{"job_id": job_id},
		map[string]interface{}{"success": success},
		time.Now())
	err := i.writeAPI.WritePoint(ctx, p)
	if err != nil {
		return err
	}
	return nil
}

func (i *Influx) Read(ctx context.Context, job_id string, duration time.Duration) (bool, error) {
	// query data from influx
	query := `from(bucket: "my-bucket")
	|> range(start: -` + duration.String() + `, stop: now())
	|> filter(fn: (r) => r._measurement == "uptime" and r.job_id == "` + job_id + `")
	|> last()`
	log.Info(query)
	result, err := i.queryAPI.Query(ctx, query)
	if err != nil {
		return false, err
	}
	isSuccess := false
	for result.Next() {
		if result.TableChanged() {
			log.Infof("table: %s\n", result.TableMetadata().String())
		}
		log.Infof("row: %s\n", result.Record().String())
		isSuccess = result.Record().Value().(bool)
	}
	if result.Err() != nil {
		return false, result.Err()
	}
	return isSuccess, nil
}
