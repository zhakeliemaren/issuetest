/* eslint-disable */

declare namespace API {

  type Color = 0 | 1;
  type SyncType = 'OneWay' | 'TwoWay';

  interface Response {
    /** code */
    code?: number;
    /** data */
    data?: any;
    /** msg */
    msg?: string;
    /** success */
    success?: boolean;
    /** finished */
    finished?: boolean;
  }

  interface CreateAccountItem {
    /** domain 域账号 */
    domain: string;
    /** nickname 花名 */
    nickname: string;
    /** account 地址 */
    account: string;
    /** email 邮箱 */
    email: string;
  }

  interface CreateJobItem {
    /** github_branch GitHub分支名 */
    github_branch: string;
    /** gitlab_branch Gitlab分支名 */
    gitlab_branch: string;
    /** gitee_branch Gitee分支名 */
    gitee_branch?: string;
    /** code_china_branch CodeChina分支名 */
    code_china_branch?: string;
    /** gitlink_branch Gitlink分支名 */
    gitlink_branch?: string;
    /** 分支同步类型 */
    type: any;
  }

  interface CreateProjectItem {
    /** name 合并工程名字 */
    name: string;
    /** github_address GitHub地址 */
    github_address: string;
    /** gitlab_address Gitlab地址 */
    gitlab_address: string;
    /** gitee_address Gitee地址 */
    gitee_address?: string;
    /** code_china_address CodeChina地址 */
    code_china_address?: string;
    /** gitlink_address Gitlink */
    gitlink_address?: string;
  }

  interface GithubAccountList {
    /** total */
    total: number;
    /** list */
    list: GithubAccount[];
  }

  interface JobList {
    /** total */
    total: number;
    /** list */
    list: Job[];
  }

  interface ProjectList {
    /** total */
    total: number;
    /** list */
    list: Project[];
  }

  interface PullRequestList {
    /** total */
    total: number;
    /** list */
    list: PullRequest[];
  }

  interface GithubAccount {
    /* id */
    id: number;
    /** domain */
    domain: string;
    /** nickname */
    nickname: string;
    /** account */
    account: string;
    /** email */
    email: string;
  }

  interface Job {
    /** id */
    id: number;
    /** project */
    project: string;
    status: Color;
    /** github_branch */
    github_branch: string;
    /** gitee_branch */
    gitee_branch?: string;
    /** gitlab_branch */
    gitlab_branch: string;
    /** code_china_branch */
    code_china_branch?: string;
    /** gitlink_branch Gitlink分支名 */
    gitlink_branch?: string;
    type: string;
    commit?: string;
    base?:string;
  }

  interface AccountListResponse {
    /** code */
    code?: number;
    data?: GithubAccountList;
    /** msg */
    msg?: string;
    /** success */
    success?: boolean;
    /** finished */
    finished?: boolean;
  }

  interface JobListResponse {
    /** code */
    code?: number;
    data?: JobList;
    /** msg */
    msg?: string;
    /** success */
    success?: boolean;
    /** finished */
    finished?: boolean;
  }

  interface ProjectListResponse {
    /** code */
    code?: number;
    data?: ProjectList;
    /** msg */
    msg?: string;
    /** success */
    success?: boolean;
    /** finished */
    finished?: boolean;
  }

  interface PullRequestListResponse {
    /** code */
    code?: number;
    data?: PullRequestList;
    /** msg */
    msg?: string;
    /** success */
    success?: boolean;
    /** finished */
    finished?: boolean;
  }

  interface LogListResponse {
    /** code */
    code?: number;
    data?: Log[];
    /** msg */
    msg?: string;
    /** success */
    success?: boolean;
    /** finished */
    finished?: boolean;
  }

  interface UserInfoResponse {
    /** code */
    code?: number;
    data?: UserInfoDto;
    /** msg */
    msg?: string;
    /** success */
    success?: boolean;
    /** finished */
    finished?: boolean;
  }

  interface Project {
    /** id */
    id: number;
    /** name */
    name: string;
    /** github_address */
    github_address: string;
    /** gitee_address */
    gitee_address?: string;
    /** gitlab_address */
    gitlab_address: string;
    /** code_china_address */
    code_china_address?: string;
     /** gitlink_address Gitlink */
     gitlink_address?: string;
  }

  interface PullRequest {
    /** id */
    id: number;
    /** title */
    title: string;
    /** project */
    project: string;
    /** type */
    type: string;
    /** address */
    address: string;
    /** author */
    author: string;
    /** email */
    email: string;
    /** target_branch */
    target_branch: string;
    /** before_commit */
    before_commit: string;
    /** merge_commit */
    merge_commit: string;
  }

  interface Log {
    /** id */
    id: number;
    /** sync_job_id */
    sync_job_id: number;
    /** log_type */
    log_type: string;
    /** log */
    log: string;
    create_time: string;
  }

  interface UserInfoDto {
    /** name 用户登录名 */
    name: string;
    /** nick 花名 */
    nick: string;
    /** emp_id 工号 */
    emp_id: any;
    /** email 用户邮箱 */
    email?: string;
    /** dept 用户部门 */
    dept?: string;
  }

  interface UpdateAccountItem {
    /** domain */
    'domain'
    : string;
    /** nickname */
    'nickname'
    : string;
    /** account */
    'account'
    : string;
    /** email */
    'email'
    : string;
    /** id */
    'id'
    : number;
  }

}
