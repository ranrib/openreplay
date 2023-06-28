package redis

import "time"

type Config struct {
	ConnectionURL     string        `env:"REDIS_STRING,required"`
	MaxLength         int64         `env:"REDIS_STREAMS_MAX_LEN,default=100000"`
	ReadCount         int64         `env:"REDIS_STREAMS_READ_COUNT,default=1"`
	ReadBlockDuration time.Duration `env:"REDIS_STREAMS_READ_BLOCK_DURATION,default=200ms"`
	CloseTimeout      time.Duration `env:"REDIS_STREAMS_CLOSE_TIMEOUT,default=5s"`
}
