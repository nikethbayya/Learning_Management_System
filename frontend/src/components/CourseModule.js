import { Grid } from "@mui/material";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemText from "@mui/material/ListItemText";
import axios from "axios";
import { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import { Link, useParams } from "react-router-dom";
import CreateModule from "./CreateModule";

function CourseModule() {
  const [isCreateMode, setIsCreateMode] = useState(false);
  const [courseModules, setCourseModules] = useState([]);
  const [createModeLabel, setCreateModeLabel] = useState("Create module");
  const { id } = useParams();
  const { role } = useSelector((state) => state.user.userInfo);

  useEffect(() => {
    axios
      .get("/course/" + id + "/modules")
      .then((resp) => {
        const { modules } = resp.data;
        console.log(modules);
        setCourseModules(modules);
      })
      .catch((err) => {
        console.log(err);
      });
  }, [isCreateMode]);

  return (
    <Box sx={{ display: "flex", flexWrap: "wrap" }}>
      {role === "Instructor" && (
        <Button
          color="primary"
          onClick={() => {
            setIsCreateMode(!isCreateMode);
            setCreateModeLabel(isCreateMode ? "Create module" : "View modules");
          }}
        >
          {createModeLabel}
        </Button>
      )}
      <Grid container spacing={1} style={{ margin: "auto" }}>
        <Grid
          item
          xs={4}
          style={{ margin: "auto", display: isCreateMode ? "none" : "block" }}
        >
          {courseModules.length === 0 && <div>No modules</div>}
          {courseModules.length > 0 && (
            <div>
              <h3>All modules</h3>
              <List>
                {courseModules.map((module, index) => {
                  return (
                    <ListItem key={index}>
                      <Link to={"/course/" + id + "/module/" + module.id}>
                        <ListItemText primary={module.name} />
                      </Link>
                    </ListItem>
                  );
                })}
              </List>
            </div>
          )}
        </Grid>
        <Grid
          item
          xs={8}
          style={{ margin: "auto", display: isCreateMode ? "none" : "block" }}
        >
          Module content
        </Grid>
        <Grid
          item
          xs={8}
          style={{ margin: "auto", display: !isCreateMode ? "none" : "block" }}
        >
          <CreateModule />
        </Grid>
      </Grid>
    </Box>
  );
}

export default CourseModule;
