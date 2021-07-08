package main

import (
	"encoding/base64"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"

	"github.com/urfave/cli"
	"github.com/ybbus/jsonrpc"
)

var Version = "dev"

func getSpec(client *http.Client, endpoint string, user string, password string) map[string]interface{} {
	req, err := http.NewRequest("GET", endpoint+"/spec", nil)
	checkErr(err)
	req.SetBasicAuth(user, password)
	resp, err := client.Do(req)
	checkErr(err)
	defer resp.Body.Close()
	bodyBytes, _ := ioutil.ReadAll(resp.Body)
	var result map[string]interface{}
	json.Unmarshal(bodyBytes, &result)
	return result
}

func exitErr(err string) {
	fmt.Println(err)
	os.Exit(1)
}

func checkErr(err error) {
	if err != nil {
		exitErr("Error: " + err.Error())
	}
}

func jsonEncode(data interface{}) string {
	b, err := json.MarshalIndent(data, "", "  ")
	checkErr(err)
	return string(b)
}

func main() {
	COINS := map[string]string{
		"btc":  "http://localhost:5000",
		"ltc":  "http://localhost:5001",
		"gzro": "http://localhost:5002",
		"bsty": "http://localhost:5003",
		"bch":  "http://localhost:5004",
		"xrg":  "http://localhost:5005",
	}
	app := cli.NewApp()
	app.Name = "Bitcart CLI"
	app.Version = Version
	app.HideHelp = true
	app.Usage = "Call RPC methods from console"
	app.UsageText = "bitcart-cli method [args]"
	app.Flags = []cli.Flag{
		&cli.BoolFlag{
			Name:    "help",
			Aliases: []string{"h"},
			Usage:   "show help",
		},
		&cli.StringFlag{
			Name:     "wallet",
			Aliases:  []string{"w"},
			Usage:    "specify wallet",
			Required: false,
			EnvVars:  []string{"BITCART_WALLET"},
		},
		&cli.StringFlag{
			Name:    "coin",
			Aliases: []string{"c"},
			Usage:   "specify coin to use",
			Value:   "btc",
			EnvVars: []string{"BITCART_COIN"},
		},
		&cli.StringFlag{
			Name:    "user",
			Aliases: []string{"u"},
			Usage:   "specify daemon user",
			Value:   "electrum",
			EnvVars: []string{"BITCART_LOGIN"},
		},
		&cli.StringFlag{
			Name:    "password",
			Aliases: []string{"p"},
			Usage:   "specify daemon password",
			Value:   "electrumz",
			EnvVars: []string{"BITCART_PASSWORD"},
		},
		&cli.StringFlag{
			Name:     "url",
			Aliases:  []string{"U"},
			Usage:    "specify daemon URL (overrides defaults)",
			Required: false,
			EnvVars:  []string{"BITCART_DAEMON_URL"},
		},
	}
	app.Action = func(c *cli.Context) error {
		args := c.Args()
		if args.Len() >= 1 {
			// load flags
			wallet := c.String("wallet")
			user := c.String("user")
			password := c.String("password")
			coin := c.String("coin")
			url := c.String("url")
			if url == "" {
				url = COINS[coin]
			}
			httpClient := &http.Client{}
			// initialize rpc client
			rpcClient := jsonrpc.NewClientWithOpts(url, &jsonrpc.RPCClientOpts{
				HTTPClient: httpClient,
				CustomHeaders: map[string]string{
					"Authorization": "Basic " + base64.StdEncoding.EncodeToString([]byte(user+":"+password)),
				},
			})
			// some magic to make array with the last element being a dictionary with xpub in it
			sl := args.Slice()[1:]
			params := make([]interface{}, len(sl))
			for i := range sl {
				params[i] = sl[i]
			}
			params = append(params, map[string]interface{}{"xpub": wallet})
			// call RPC method
			result, err := rpcClient.Call(args.Get(0), params)
			checkErr(err)
			// Print either error if found or result
			if result.Error != nil {
				spec := getSpec(httpClient, url, user, password)
				if spec["error"] != nil {
					exitErr(jsonEncode(spec["error"]))
				}
				exceptions := spec["exceptions"].(map[string]interface{})
				errorCode := fmt.Sprint(result.Error.Code)
				if exception, ok := exceptions[errorCode]; ok {
					exception, _ := exception.(map[string]interface{})
					exitErr(exception["exc_name"].(string) + ": " + exception["docstring"].(string))
				}
				exitErr(jsonEncode(result.Error))
			} else {
				fmt.Println(jsonEncode(result.Result))
				return nil
			}
		} else {
			cli.ShowAppHelp(c)
		}
		return nil
	}
	err := app.Run(os.Args)
	checkErr(err)
}
