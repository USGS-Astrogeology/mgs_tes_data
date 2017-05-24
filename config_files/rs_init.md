```
rs.initiate(
  {
    _id: "configsvr",
    configsvr: true,
    members: [
      { _id : 0, host : "configsvr-tes-mongodb.marathon.containerip.dcos.thisdcos.directory:27019" }
    ]
  }
)

rs.initiate(
  {
    _id: "shard1",
    members: [
      { _id : 0, host : "shard1-tes-mongodb.marathon.containerip.dcos.thisdcos.directory:27020" }
    ]
  }
)


rs.initiate(
  {
    _id: "shard2",
    members: [
      { _id : 0, host : "shard2-tes-mongodb.marathon.containerip.dcos.thisdcos.directory:27021" }
    ]
  }
)

rs.initiate(
  {
    _id: "shard3",
    members: [
      { _id : 0, host : "shard3-tes-mongodb.marathon.containerip.dcos.thisdcos.directory:27022" }
    ]
  }
)



sh.addShard( "shard1/shard1-tes-mongodb.marathon.containerip.dcos.thisdcos.directory:27018")



configsvr/configsvr-tes-mongodb.marathon.containerip.dcos.thisdcos.directory
```
