package influx

import (
	"context"
	"strings"
	"time"

	influxdb2 "github.com/influxdata/influxdb-client-go/v2"
	"github.com/influxdata/influxdb-client-go/v2/api"
	"github.com/skyface753/cronitor_selfhost/config"
	log "github.com/skyface753/cronitor_selfhost/skyLog"
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

func (i *Influx) InsertUptime(ctx context.Context, config *config.Config, job_id string, success bool, content string) error {
	p := influxdb2.NewPointWithMeasurement("uptime").
		AddTag("job_id", job_id).
		AddField("success", success).
		AddField("content", content).
		SetTime(time.Now())
	err := i.writeAPI.WritePoint(ctx, p)
	if err != nil {
		return err
	}
	return nil
}

func (i *Influx) Read(ctx context.Context, config *config.Config, job_id string, duration time.Duration) (bool, string, error) {
	// query data from influx
	query := `from(bucket: "my-bucket")
	|> range(start: -` + duration.String() + `, stop: now())
	|> filter(fn: (r) => r._measurement == "uptime" and r.job_id == "` + job_id + `")
	|> last()`
	// log.Info(query)
	result, err := i.queryAPI.Query(ctx, query)
	if err != nil {
		return false, "", err
	}
	isSuccess := false
	content := ""
	for result.Next() {
		if result.Record().Field() == "success" {
			isSuccess = result.Record().Value().(bool)
		} else if result.Record().Field() == "content" {
			content = result.Record().Value().(string)
		} else {
			log.Error("Unknown field: ", result.Record().Field())
		}
	}
	// log.Info("success: ", isSuccess, " content: ", content)
	if result.Err() != nil {
		return false, "", result.Err()
	}
	return isSuccess, content, nil
}

func (i *Influx) GetAllLastForAllJobs(ctx context.Context, config *config.Config) (map[string]map[string]interface{}, error) {
	// query data from influx
	query := `from(bucket: "my-bucket")
	|> range(start: -24h, stop: now())
	|> filter(fn: (r) => r._measurement == "uptime")
	|> last()`
	log.Info(strings.ReplaceAll(strings.ReplaceAll(query, "\n", ""), "\t", ""))

	result, err := i.queryAPI.Query(ctx, query)
	// Putting back the data in share requires a bit of work
	var resultPoints = make(map[string]map[string]interface{})

	if err == nil {
		// Iterate over query response
		for result.Next() {
			// Notice when group key has changed
			if result.TableChanged() {
				log.Info("table: ", result.TableMetadata().String())
			}

			// val, ok := resultPoints[result.Record().Time()]

			val, ok := resultPoints[result.Record().ValueByKey("job_id").(string)]

			if !ok {
				val = make(map[string]interface{})

			}

			switch field := result.Record().Field(); field {
			case "success":
				// val.avg = result.Record().Value().(float64)
				val["success"] = result.Record().Value().(bool)
			case "content":
				// val.max = result.Record().Value().(float64)
				val["content"] = result.Record().Value().(string)
			default:
				log.Error("unrecognized field ", field)
			}

			// resultPoints[result.Record().Time()] = val
			resultPoints[result.Record().ValueByKey("job_id").(string)] = val

		}
		// check for an error
		if result.Err() != nil {
			log.Error("query parsing error: ", result.Err().Error())
		}
	} else {
		panic(err)
	}
	return resultPoints, err
}

// Type for the data returned by GetAllForJob
type UptimeData struct {
	Success bool
	Content string
}
type UptimeDataMap map[time.Time]UptimeData

type UptimeDataForAllJobsMap map[string]UptimeDataMap

func (i *Influx) GetAllForJob(ctx context.Context, config *config.Config, jobID string) (UptimeDataMap, error) {
	// query data from influx
	query := `from(bucket: "my-bucket")
	|> range(start: -24h, stop: now())
	|> filter(fn: (r) => r._measurement == "uptime" and r.job_id == "` + jobID + `")`

	// Log query without \n and \t
	log.Info(strings.ReplaceAll(strings.ReplaceAll(query, "\n", ""), "\t", ""))
	result, err := i.queryAPI.Query(ctx, query)

	// var resultPoints = make(map[time.Time]map[string]interface{})
	var resultPoints = make(map[time.Time]UptimeData)
	if err == nil {
		// Iterate over query response
		for result.Next() {
			// Notice when group key has changed
			if result.TableChanged() {
				// fmt.Printf("table: %s\n", result.TableMetadata().String())
				log.Info("table: ", result.TableMetadata().String())
			}

			val, ok := resultPoints[result.Record().Time()]

			if !ok {
				// val = make(map[string]interface{})
				val = UptimeData{}

			}

			switch field := result.Record().Field(); field {
			case "success":
				// val["success"] = result.Record().Value().(bool)
				val.Success = result.Record().Value().(bool)
			case "content":
				// val["content"] = result.Record().Value().(string)
				val.Content = result.Record().Value().(string)
			default:
				log.Error("unrecognized field ", field)
			}

			resultPoints[result.Record().Time()] = val

		}
		// check for an error
		if result.Err() != nil {
			log.Error("query parsing error: ", result.Err().Error())
		}
	} else {
		panic(err)
	}
	return resultPoints, err
}

func (i *Influx) GetAllForAll(ctx context.Context) (UptimeDataForAllJobsMap, error) {
	// query data from influx
	query := `from(bucket: "my-bucket")
	|> range(start: -24h, stop: now())
	|> filter(fn: (r) => r._measurement == "uptime")`

	// Log query without \n and \t
	log.Info(strings.ReplaceAll(strings.ReplaceAll(query, "\n", ""), "\t", ""))
	result, err := i.queryAPI.Query(ctx, query)

	// var resultPoints = make(map[time.Time]map[string]interface{})
	var resultPoints = make(map[string]UptimeDataMap)
	if err == nil {
		// Iterate over query response
		for result.Next() {
			// Notice when group key has changed
			if result.TableChanged() {
				// fmt.Printf("table: %s\n", result.TableMetadata().String())
				log.Info("table: ", result.TableMetadata().String())
			}

			val, ok := resultPoints[result.Record().ValueByKey("job_id").(string)]

			if !ok {
				// val = make(map[string]interface{})
				val = UptimeDataMap{}

			}

			switch field := result.Record().Field(); field {
			case "success":
				// val["success"] = result.Record().Value().(bool)
				val[result.Record().Time()] = UptimeData{Success: result.Record().Value().(bool)}
			case "content":
				// val["content"] = result.Record().Value().(string)
				val[result.Record().Time()] = UptimeData{Content: result.Record().Value().(string)}
			default:
				log.Error("unrecognized field ", field)
			}

			resultPoints[result.Record().ValueByKey("job_id").(string)] = val

		}
		// check for an error
		if result.Err() != nil {
			log.Error("query parsing error: ", result.Err().Error())
		}
	} else {
		panic(err)
	}
	return resultPoints, err
}
